from django.contrib import admin

from lessons.models import Course, Lesson, Payment, Subscription


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'owner',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'url_video', 'course', 'owner',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_data', 'paid_course', 'paid_lesson', 'summ', 'payment_method')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'is_active',)




