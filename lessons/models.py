from django.db import models

from users.models import NULLABLE


class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name='название')
    preview = models.ImageField(upload_to='courses/preview', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)

    class Meta:
        verbose_name = 'курс'
        verbose_name_plural = 'курсы'


class Lesson(models.Model):
    title = models.CharField(max_length=255, verbose_name='название')
    preview = models.ImageField(upload_to='courses/preview', verbose_name='превью', **NULLABLE)
    description = models.TextField(verbose_name='описание', **NULLABLE)
    url_video = models.TextField(verbose_name='ссылка на видео', **NULLABLE)

    class Meta:
        verbose_name = 'урок'
        verbose_name_plural = 'уроки'

