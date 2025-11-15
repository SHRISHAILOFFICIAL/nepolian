from django.db import models
from django.utils import timezone
from apps.user_authentication.models import CustomUser


class Store(models.Model):
    """Store/Location model"""
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='managed_stores')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"


class Shift(models.Model):
    """Shift posting model"""
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    ROLE_CHOICES = [
        ('cashier', 'Cashier'),
        ('stocker', 'Stocker'),
        ('sales_associate', 'Sales Associate'),
        ('supervisor', 'Supervisor'),
        ('cleaner', 'Cleaner'),
    ]
    
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shifts')
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_shifts')
    title = models.CharField(max_length=200)
    description = models.TextField()
    role_required = models.CharField(max_length=50, choices=ROLE_CHOICES)
    shift_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slots_available = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-shift_date', '-start_time']
    
    def __str__(self):
        return f"{self.title} - {self.store.name} on {self.shift_date}"
    
    def is_past(self):
        """Check if shift date is in the past"""
        return self.shift_date < timezone.now().date()
    
    def available_slots(self):
        """Calculate available slots"""
        approved_count = self.volunteers.filter(status='approved').count()
        return self.slots_available - approved_count
    
    def can_volunteer(self, user):
        """Check if user can volunteer for this shift"""
        if self.status != 'open':
            return False
        if self.is_past():
            return False
        if self.available_slots() <= 0:
            return False
        if self.volunteers.filter(volunteer=user).exists():
            return False
        return True


class ShiftVolunteer(models.Model):
    """Volunteer applications for shifts"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='volunteers')
    volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shift_applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_applications')
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-applied_at']
        unique_together = ['shift', 'volunteer']
    
    def __str__(self):
        return f"{self.volunteer.username} - {self.shift.title} ({self.status})"


class ShiftHistory(models.Model):
    """Track shift changes for audit purposes"""
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
    ]
    
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.shift.title} - {self.action} by {self.performed_by}"
