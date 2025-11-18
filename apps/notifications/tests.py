from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.notifications.models import Notification

User = get_user_model()


class NotificationViewTestCase(TestCase):
    """Test notification views"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123',
            role='staff'
        )
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test Notification',
            message='This is a test message',
            notification_type='info'
        )

    def test_notification_list_requires_login(self):
        """Test notification list requires authentication"""
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_notification_list_authenticated(self):
        """Test authenticated user can access notification list"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Notification')
    
    def test_mark_all_read_requires_login(self):
        """Test mark all read requires authentication"""
        response = self.client.post('/notifications/mark-all-read/')
        self.assertEqual(response.status_code, 302)
    
    def test_mark_all_read_authenticated(self):
        """Test authenticated user can mark all as read"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.post('/notifications/mark-all-read/')
        # Should redirect back to notifications page
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        
    def test_mark_as_read(self):
        """Test marking single notification as read"""
        self.client.login(username='testuser', password='pass123')
        response = self.client.post(f'/notifications/{self.notification.id}/read/')
        self.assertEqual(response.status_code, 302)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        
    def test_unread_notifications_count(self):
        """Test counting unread notifications"""
        # Create another unread notification
        Notification.objects.create(
            recipient=self.user,
            title='Another Notification',
            message='Another test message',
            notification_type='warning'
        )
        self.client.login(username='testuser', password='pass123')
        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)
        
    def test_notification_model_str(self):
        """Test notification string representation"""
        self.assertIn('Test Notification', str(self.notification))
