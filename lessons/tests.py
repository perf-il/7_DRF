from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import AccessToken

from lessons.models import Course, Lesson, Subscription
from users.models import User


class LessonsTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            email='test@test.ts',
            password='1111',
            is_superuser=True,
            is_staff=True,
            is_active=True,
        )
        self.client = APIClient()
        token = AccessToken.for_user(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def test_create_course(self):
        """Тестирование создания нового курса"""
        data = {
            'title': 'Test Course',
            'description': 'Test description',
            'owner': self.user.pk,
        }

        response = self.client.post(
            reverse('lessons:courses'),
            data=data
        )
        print('-->!', response)

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

    def test_create_lesson(self):
        """Тестирование создания нового урока"""

        self.course = Course.objects.create(
            title='Test course',
            description='test description'
        )
        data = {
            'title': 'Test create lesson',
            'preview': '',
            'description': 'Test description',
            'url_video': 'https://www.youtube.com/',
            'course': self.course.pk,
            'owner': self.user.pk

        }

        response = self.client.post(
            reverse('lessons:lesson-create'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            Lesson.objects.all().exists()
        )

        self.assertEqual(
            response.json(),
            {
                'id': 1,
                'title': 'Test create lesson',
                'preview': None,
                'description': 'Test description',
                'url_video': 'https://www.youtube.com/',
                'course': self.course.pk,
                'owner': self.user.pk
            }
        )

    def test_list_lesson(self):
        """Тестирование списка уроков"""

        self.lesson = Lesson.objects.create(
            title='Test lesson',
            description='test description',
            url_video='https://www.youtube.com/',

        )

        response = self.client.get(
            reverse('lessons:all-lessons')

        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json()['results'],
            [
                {'id': self.lesson.id,
                 'title': self.lesson.title,
                 'preview': None,
                 'description': self.lesson.description,
                 'url_video': self.lesson.url_video,
                 'course': None,
                 'owner': None}
            ]
        )

    def test_update_lesson(self):
        """Тестирование редактирования урока"""

        self.lesson = Lesson.objects.create(
            title='Test lesson',
            description='test description',
            url_video='https://www.youtube.com/',

        )

        data = {
            'title': 'Test update lesson',
            'description': 'Test update description',
        }

        response = self.client.put(
            reverse('lessons:lesson-update', kwargs={"pk": self.lesson.pk}),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.json()['title'],
            'Test update lesson'
        )

        self.assertEqual(
            response.json()['description'],
            'Test update description'
        )

    def test_delete_lesson(self):
        """Тестирование удаления урока"""

        self.lesson = Lesson.objects.create(
            title='Test lesson',
            description='test description',
            url_video='https://www.youtube.com/',

        )

        self.assertTrue(
            Lesson.objects.all().exists()
        )

        self.client.delete(
            reverse('lessons:lesson-delete', kwargs={"pk": self.lesson.pk}),
        )

        self.assertFalse(
            Lesson.objects.all().exists()
        )

    def test_bad_url_lesson(self):
        """Тестирование валидации ссылки на урок"""

        data = {
            'title': 'Test bad url lesson',
            'preview': '',
            'description': 'Test description',
            'url_video': 'https://www.badurl.com/',

        }

        response = self.client.post(
            reverse('lessons:lesson-create'),
            data=data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            *response.json()['non_field_errors'],
            f"Ссылка {data['url_video']} является недопустимой"

        )

        self.assertFalse(
            Lesson.objects.all().exists()
        )

    def test_subscription(self):
        """Тестирование функционала подписки/отписки урока"""

        self.course = Course.objects.create(
            title='Test course',
            description='test description')

        self.assertFalse(Subscription.objects.all().exists())
        self.client.post(
            reverse('lessons:course-subscribe', kwargs={'pk': self.course.pk}),
        )
        self.assertTrue(Subscription.objects.all().exists())

        self.subscription = Subscription.objects.all()[0]
        self.assertEqual(
            self.subscription.__str__(),
            f'{self.user.email} подписан на курс {self.course.title}'
        )

        self.client.delete(
            reverse('lessons:course-unsubscribe', kwargs={'pk': self.subscription.pk}),
        )

        self.unsubscription = Subscription.objects.all()[0]
        self.assertEqual(
            self.unsubscription.__str__(),
            f'{self.user.email} отписался от курса {self.course.title}'
        )

