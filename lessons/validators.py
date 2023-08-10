import re

from rest_framework.exceptions import ValidationError


class URLValidator:

    def __init__(self, field):
        self.field = field

    def __call__(self, value):
        domen = re.compile(r"https://www.youtube.com/")
        tmp_val = dict(value).get(self.field)
        if tmp_val and not bool(domen.match(tmp_val)):
            raise ValidationError(f'Ссылка {tmp_val} является недопустимой')
