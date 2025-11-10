from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser
from django.db import IntegrityError

class CustomUserModelTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='staff'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.role, 'staff')
        self.assertTrue(self.user.is_active)

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser (Staff)')

    def test_user_email_unique(self):
        with self.assertRaises(IntegrityError):
            CustomUser.objects.create_user(
                username='testuser2',
                email='test@example.com',
                password='pass123'
            )

class AuthenticationViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login

    def test_user_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
