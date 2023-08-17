from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response


from lessons.models import Course, Lesson, Payment, Subscription
from lessons.pagination import MyPagination
from lessons.permissions import IsModerator, IsOwner, IsNotModerator, IsOwnerOrModerator
from lessons.serializers import CourseSerializer, LessonSerializer, PaymentSerializer, SubscriptionSerializer
from lessons.services import create_session, create_payment
from lessons.tasks import send_mail_course_update


class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    pagination_class = MyPagination

    def get(self, request):
        queryset = Course.objects.all()
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = CourseSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        send_mail_course_update.delay(instance.title, instance.pk)
        return Response(serializer.data)

    def get_permissions(self):

        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        elif self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsOwnerOrModerator]
        elif self.action == 'create':
            permission_classes = [IsNotModerator]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsNotModerator]


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]
    pagination_class = MyPagination

    def get(self, request):
        queryset = Lesson.objects.all()
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = LessonSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsOwnerOrModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAdminUser]


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ('paid_course', 'paid_lesson', 'payment_method')
    ordering_fields = ('payment_data',)
    permission_classes = [IsAuthenticated]
    pagination_class = MyPagination

    def get(self, request):
        queryset = Payment.objects.all()
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = PaymentSerializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class PaymentDestroyAPIView(generics.DestroyAPIView):
    queryset = Payment.objects.all()
    permission_classes = [IsAuthenticated]


class SubscriptionCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        serializer = SubscriptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        #  получение модели курса по url
        course_id = int(request.get_full_path().split('/')[3])
        course = Course.objects.get(id=course_id)
        #  проверка существования ранее созданной подписки в активном статусе
        #  при выполнении условия выполняется исключение
        if Subscription.objects.filter(user=request.user, course=course, is_active=True).exists():
            raise Exception('Вы уже подписаны на этот курс')
        #  создание новой платежной сессии и модели платежа
        payment_data = create_session(course)
        create_payment(request, payment_data, course)
        #  проверка существования ранее созданной подписки в неактивном статусе
        #  при выполнении условия статус меняется на активный
        if Subscription.objects.filter(user=request.user, course=course, is_active=False).exists():
            sub = Subscription.objects.filter(user=request.user, course=course, is_active=False)[0]
            sub.is_active = True
            sub.save()
        else:
            try:
                serializer.save(user=request.user, course=course)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(f'Курс с id = {course_id} не существует')
            except:
                raise Exception('Создание подписки невозможно')
        return Response(data={'id': payment_data.get('id'), 'url': payment_data.get('url')}, status=status.HTTP_201_CREATED)


class SubscriptionDestroyAPIView(generics.DestroyAPIView):
    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user == self.request.user or self.request.user.is_superuser:
            instance.is_active = False
            instance.is_paid = False
            instance.save()
        else:
            raise Exception('Вы не можете удалить эту подписку')