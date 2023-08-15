from django.core.management import BaseCommand

from lessons.models import Payment, Subscription
from lessons.services import get_payment_status


class Command(BaseCommand):

    def handle(self, *args, **options):
        all_payments = Payment.objects.all()

        for payment in all_payments:
            current_status = get_payment_status(payment.stripe_id)
            if not current_status:
                continue
            if current_status != payment.status:
                payment.status = current_status
                payment.save()
                sub = Subscription.objects.filter(course=payment.paid_course, user=payment.user)[0]
                sub.is_paid = True
                sub.save()
