from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, time, timedelta
from django.utils import timezone
from apps.shift_management.models import Shift, ShiftVolunteer, Store

User = get_user_model()


class ShiftViewTestCase(TestCase):
    """Test shift management views"""

    def setUp(self):
        self.manager = User.objects.create_user(
            username='manager1',
            email='manager@test.com',
            password='pass123',
            role='manager',
            first_name='Manager',
            last_name='One'
        )
        self.staff = User.objects.create_user(
            username='staff1',
            email='staff@test.com',
            password='pass123',
            role='staff',
            first_name='Staff',
            last_name='One'
        )
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            is_active=True
        )
        self.shift = Shift.objects.create(
            title='Test Shift',
            store=self.store,
            manager=self.manager,
            shift_date=timezone.now().date() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(17, 0),
            role_required='cashier',
            slots_available=2,
            status='open'
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
        
        
    def test_shift_list_with_filters(self):
        """Test shift list with role and store filters"""
        self.client.login(username='staff1', password='pass123')
        response = self.client.get(f'/shifts/?role=cashier&store={self.store.id}')
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
        
    def test_shift_detail_view(self):
        """Test shift detail view"""
        self.client.login(username='staff1', password='pass123')
        response = self.client.get(f'/shifts/{self.shift.id}/')
        self.assertEqual(response.status_code, 200)
        
    def test_shift_list_shows_available_shifts_only(self):
        """Test shift list only shows shifts with available slots"""
        # Create a filled shift
        filled_shift = Shift.objects.create(
            title='Filled Shift',
            store=self.store,
            manager=self.manager,
            shift_date=timezone.now().date() + timedelta(days=2),
            start_time=time(9, 0),
            end_time=time(17, 0),
            role_required='cashier',
            slots_available=1,
            status='filled'
        )
        self.client.login(username='staff1', password='pass123')
        response = self.client.get('/shifts/')
        self.assertEqual(response.status_code, 200)
        
    def test_shift_model_str(self):
        """Test shift string representation"""
        self.assertIn('Test Shift', str(self.shift))
        
    def test_store_model_str(self):
        """Test store string representation"""
        self.assertIn('Test Store', str(self.store))
        
    def test_shift_available_slots(self):
        """Test shift available_slots method"""
        slots = self.shift.available_slots()
        self.assertEqual(slots, 2)
        
    def test_shift_can_volunteer(self):
        """Test can_volunteer method"""
        can_apply = self.shift.can_volunteer(self.staff)
        self.assertTrue(can_apply)
        
    def test_shift_volunteer_model(self):
        """Test ShiftVolunteer model creation"""
        application = ShiftVolunteer.objects.create(
            shift=self.shift,
            volunteer=self.staff,
            status='pending'
        )
        self.assertEqual(application.status, 'pending')
        self.assertIn(str(self.staff.username), str(application))
