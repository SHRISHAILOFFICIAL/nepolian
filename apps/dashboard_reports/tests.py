from django.test import TestCase, Client
from django.urls import reverse
from apps.user_authentication.models import CustomUser


class DashboardViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = CustomUser.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='pass123',
            role='admin'
        )
        self.manager_user = CustomUser.objects.create_user(
            username='manager',
            email='manager@test.com',
            password='pass123',
            role='manager'
        )
        self.staff_user = CustomUser.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='pass123',
            role='staff'
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_admin_dashboard_access(self):
        self.client.login(username='admin', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_manager_dashboard_access(self):
        self.client.login(username='manager', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_staff_dashboard_access(self):
        self.client.login(username='staff', password='pass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
