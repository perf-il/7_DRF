import requests

from config import settings
from lessons.models import Course, Payment


def create_product(name):
    """Создание продукта на платформе Stripe"""
    url = 'https://api.stripe.com/v1/products'
    headers = {
        'Authorization': f'Bearer {settings.STRIP_API_KEY}'
    }
    params = {
        'name': name
    }

    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('id')


def create_price(product_name, price, interval='month', currency='USD'):
    """Создание стоимости продукта на платформе Stripe"""
    url = 'https://api.stripe.com/v1/prices'
    headers = {
        'Authorization': f'Bearer {settings.STRIP_API_KEY}'
    }
    params = {
        'unit_amount': price,
        'currency': currency,
        'recurring[interval]': interval,
        'product': create_product(product_name)
    }

    response = requests.post(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get('id')


def create_session(model: Course):
    """Создание платежной сессии на платформе Stripe"""
    url = 'https://api.stripe.com/v1/checkout/sessions'
    headers = {
        'Authorization': f'Bearer {settings.STRIP_API_KEY}'
    }
    params = {
        'mode': 'subscription',
        'line_items[0][price]': create_price(model.title, model.price),
        'line_items[0][quantity]': 1,

        'success_url': 'https://example.com/success',
    }

    response = requests.post(url, headers=headers, params=params)

    return response.json()


def get_payment_status(id_payment):
    """Функция для получения статуса платежа по id-номеру платежной сессии"""
    url = f'https://api.stripe.com/v1/checkout/sessions/{id_payment}'
    headers = {
        'Authorization': f'Bearer {settings.STRIP_API_KEY}'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json().get('payment_status')


def create_payment(instance, payment_data, course):
    """Создание нового платежа (модель Payment)"""
    Payment.objects.create(
        user=instance.user,
        paid_course=course,
        summ=payment_data.get('amount_total'),
        payment_method='CL',
        stripe_id=payment_data.get('id'),
        status=get_payment_status(payment_data.get('id'))
    )



