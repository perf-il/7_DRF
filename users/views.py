from django.shortcuts import render
from rest_framework import viewsets

from users.models import User
from users.serializers import UsersSerializer


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UsersSerializer
    queryset = User.objects.all()
