from django.db import models
from apps.user_authentication.models import CustomUser


class Notification(models.Model):
    """In-app notification system"""
    TYPE_CHOICES = [
        ('shift_created', 'Shift Created'),
        ('shift_updated', 'Shift Updated'),
        ('shift_cancelled', 'Shift Cancelled'),
        ('application_approved', 'Application Approved'),
        ('application_rejected', 'Application Rejected'),
        ('new_application', 'New Application'),
        ('system', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient.username} - {self.title}"
