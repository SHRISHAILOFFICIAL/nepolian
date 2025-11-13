from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTestCase(TestCase):
    """Test custom user model"""

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            role='staff'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(user.role, 'staff')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_str(self):
        """Test string representation"""
        user = User.objects.create_user(
            username='staff1',
            email='staff@test.com',
            password='pass123',
            role='staff'
        )
        self.assertIn('staff1', str(user))


class AuthViewTestCase(TestCase):
    """Test authentication views"""

    def test_login_page_accessible(self):
        """Test login page loads"""
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 200)

    def test_signup_page_accessible(self):
        """Test signup page loads"""
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)
