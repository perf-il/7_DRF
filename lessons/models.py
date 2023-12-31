from django.db import models
from django.db.models import TextChoices

from users.models import NULLABLE, User


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='название')
    preview = models.ImageField(upload_to='courses/preview', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='автор', related_name='course_author', **NULLABLE)
    price = models.PositiveIntegerField(default=1000, verbose_name='цена')

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'

    def __str__(self):
        return self.title


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='название')
    preview = models.ImageField(upload_to='courses/preview', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)
    url_video = models.TextField(verbose_name='ссылка на видео', **NULLABLE)
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name='курс', related_name='lesson', **NULLABLE)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='автор', related_name='lesson_author', **NULLABLE)

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'

    def __str__(self):
        return f'Урок "{self.title}"'


class Payment(models.Model):
    class MethodPayment(TextChoices):
        CASH = 'CA', 'Cash'
        CASHLESS = 'CL', 'Cashless'

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    payment_data = models.DateField(auto_now_add=True,verbose_name='дата оплаты')
    paid_course = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name='оплаченный курс', **NULLABLE)
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, verbose_name='оплаченный урок', **NULLABLE)
    summ = models.PositiveIntegerField(verbose_name='сумма оплаты')
    payment_method = models.CharField(max_length=2, choices=MethodPayment.choices, default=MethodPayment.CASH[0],
                                      verbose_name='способ оплаты')
    stripe_id = models.CharField(max_length=330, verbose_name='id номер в системе Stripe')
    status = models.CharField(max_length=30, verbose_name='статус')

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'

    def __str__(self):
        return f'{self.user}'


class Subscription(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='курс')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    is_active = models.BooleanField(default=True, verbose_name='подписан')
    is_paid = models.BooleanField(default=False, verbose_name='оплачено')

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        unique_together = ['user', 'course']

    def __str__(self):
        return f'{self.user} подписан на курс {self.course}' if self.is_active else f'{self.user} отписался от курса {self.course}'