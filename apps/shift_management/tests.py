from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta

User = get_user_model()


class ShiftViewTestCase(TestCase):
    """Test shift management views"""

    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager1',
            email='manager@test.com',
            password='pass123',
            role='manager'
        )
        self.staff = User.objects.create_user(
            username='staff1',
            email='staff@test.com',
            password='pass123',
            role='staff'
        )

    def test_shift_list_requires_login(self):
        """Test shift list requires authentication"""
        response = self.client.get('/shifts/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_shift_list_authenticated(self):
        """Test authenticated user can access shift list"""
        self.client.login(username='staff1', password='pass123')
        response = self.client.get('/shifts/')
        self.assertEqual(response.status_code, 200)

    def test_manager_dashboard_requires_manager_role(self):
        """Test manager dashboard requires manager role"""
        self.client.login(username='staff1', password='pass123')
        response = self.client.get('/shifts/manager/')
        self.assertEqual(response.status_code, 302)  # Redirect - access denied

    def test_manager_dashboard_accessible_by_manager(self):
        """Test manager can access manager dashboard"""
        self.client.login(username='manager1', password='pass123')
        response = self.client.get('/shifts/manager/')
        self.assertEqual(response.status_code, 200)
    
    def test_my_shifts_requires_login(self):
        """Test my shifts requires authentication"""
        response = self.client.get('/shifts/my-shifts/')
        self.assertEqual(response.status_code, 302)
    
    def test_my_shifts_accessible_when_logged_in(self):
        """Test authenticated user can access my shifts"""
        self.client.login(username='staff1', password='pass123')
        response = self.client.get('/shifts/my-shifts/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_shift_requires_manager(self):
        """Test create shift requires manager role"""
        self.client.login(username='staff1', password='pass123')
        response = self.client.get('/shifts/manager/create/')
        self.assertEqual(response.status_code, 302)
    
    def test_create_shift_accessible_by_manager(self):
        """Test manager can access create shift page"""
        self.client.login(username='manager1', password='pass123')
        response = self.client.get('/shifts/manager/create/')
        self.assertEqual(response.status_code, 200)
