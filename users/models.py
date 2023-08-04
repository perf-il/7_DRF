from django.contrib.auth.models import AbstractUser
from django.db import models


NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name='E-mail', unique=True)
    phone = models.CharField(max_length=35, verbose_name='Номер телефона', **NULLABLE)
    avatar = models.ImageField(upload_to='user_avatar/', verbose_name='Аватар', **NULLABLE)
    city = models.CharField(max_length=50, verbose_name='город', **NULLABLE)
    is_active = models.BooleanField(default=False, verbose_name='Подтверждение e-mail')

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []