from rest_framework import serializers

from lessons.models import Course, Lesson, Payment, Subscription
from lessons.validators import URLValidator


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [URLValidator(field='url_video')]


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(source='lesson', many=True, read_only=True)
    number_of_lessons = serializers.SerializerMethodField(read_only=True)
    subscription = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Course
        fields = '__all__'

    def get_number_of_lessons(self, instance):
        return instance.lesson.all().count()

    def get_subscription(self, instance):
        current_user = self.context['request'].user
        return Subscription.objects.filter(course=instance, user=current_user, is_active=True).exists()


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'


class SubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    course = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = '__all__'



