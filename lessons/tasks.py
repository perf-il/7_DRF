from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail

from config import settings
from lessons.models import Subscription
from users.models import User


@shared_task
def send_mail_course_update(course_title, course_id):
    subscriptions = [s.user for s in Subscription.objects.filter(is_active=True, course=course_id)]
    send_mail(
        subject='Уведомление об изменении курса',
        message=f'Сообщаем вам что курс "{course_title}" был изменен.',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=subscriptions
    )
    print(f'Сообщение отпралено {len(subscriptions)} пользователям --> {subscriptions}')


@shared_task
def deactivate_user_month():
    all_users =User.objects.filter(is_active=True)
    for user in all_users:
        if user.last_login <= datetime.now() - timedelta(days=5):
            user.is_active = False
            user.save()



