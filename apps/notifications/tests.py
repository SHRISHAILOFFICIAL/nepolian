from django.test import TestCase, Client
from django.urls import reverse
from apps.user_authentication.models import CustomUser
from .models import Notification


class NotificationModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123',
            role='staff'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type='shift_created',
            title='Test Notification',
            message='This is a test notification',
            link='/test/'
        )

    def test_notification_creation(self):
        self.assertEqual(self.notification.title, 'Test Notification')
        self.assertFalse(self.notification.is_read)

    def test_notification_string_representation(self):
        self.assertIn('Test Notification', str(self.notification))


class NotificationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123',
            role='staff'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            notification_type='shift_created',
            title='Test Notification',
            message='This is a test notification'
        )

    def test_notification_list_requires_login(self):
        response = self.client.get(reverse('notification_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_notification_list_authenticated(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(reverse('notification_list'))
        self.assertEqual(response.status_code, 200)

    def test_mark_notification_read(self):
        self.client.login(username='testuser', password='pass123')
        response = self.client.get(
            reverse('mark_notification_read', args=[self.notification.id])
        )
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
