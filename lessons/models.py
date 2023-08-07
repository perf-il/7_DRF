from django.db import models
from django.db.models import TextChoices

from users.models import NULLABLE, User


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='название')
    preview = models.ImageField(upload_to='courses/preview', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, verbose_name='автор', related_name='course_author', **NULLABLE)

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
    payment_data = models.DateField(verbose_name='дата оплаты', auto_now_add=True)
    paid_course = models.ForeignKey(Course, on_delete=models.SET_NULL, verbose_name='оплаченный курс', **NULLABLE)
    paid_lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, verbose_name='оплаченный урок', **NULLABLE)
    summ = models.PositiveIntegerField(verbose_name='сумма оплаты')
    payment_method = models.CharField(max_length=2, choices=MethodPayment.choices, default=MethodPayment.CASH[0],
                                      verbose_name='способ оплаты')

    class Meta:
        verbose_name = 'платеж'
        verbose_name_plural = 'платежи'

    def __str__(self):
        return f'{self.user}'
