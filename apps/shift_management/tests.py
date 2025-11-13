from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import date, time, timedelta
from apps.user_authentication.models import CustomUser
from .models import Store, Shift, ShiftVolunteer, ShiftHistory


class StoreModelTestCase(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            username='manager1',
            email='manager@test.com',
            password='pass123',
            role='manager'
        )
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            phone='555-1234',
            manager=self.manager
        )

    def test_store_creation(self):
        self.assertEqual(self.store.name, 'Test Store')
        self.assertTrue(self.store.is_active)

    def test_store_string_representation(self):
        self.assertEqual(str(self.store), 'Test Store - Test City')


class ShiftModelTestCase(TestCase):
    def setUp(self):
        self.manager = CustomUser.objects.create_user(
            username='manager1',
            email='manager@test.com',
            password='pass123',
            role='manager'
        )
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            phone='555-1234',
            manager=self.manager
        )
        self.shift = Shift.objects.create(
            store=self.store,
            manager=self.manager,
            title='Morning Shift',
            description='Morning shift duties',
            role_required='cashier',
            shift_date=date.today() + timedelta(days=1),
            start_time=time(9, 0),
            end_time=time(17, 0),
            slots_available=3
        )

    def test_shift_creation(self):
        self.assertEqual(self.shift.title, 'Morning Shift')
        self.assertEqual(self.shift.status, 'open')

    def test_shift_available_slots(self):
        self.assertEqual(self.shift.available_slots(), 3)

    def test_shift_can_volunteer(self):
        staff = CustomUser.objects.create_user(
            username='staff1',
            email='staff@test.com',
            password='pass123',
            role='staff'
        )
        self.assertTrue(self.shift.can_volunteer(staff))


class ShiftViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = CustomUser.objects.create_user(
            username='manager1',
            email='manager@test.com',
            password='pass123',
            role='manager'
        )
        self.staff = CustomUser.objects.create_user(
            username='staff1',
            email='staff@test.com',
            password='pass123',
            role='staff'
        )
        self.store = Store.objects.create(
            name='Test Store',
            address='123 Test St',
            city='Test City',
            state='TS',
            zip_code='12345',
            phone='555-1234',
            manager=self.manager
        )

    def test_shift_list_view_requires_login(self):
        response = self.client.get(reverse('shift_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_shift_list_view_authenticated(self):
        self.client.login(username='staff1', password='pass123')
        response = self.client.get(reverse('shift_list'))
        self.assertEqual(response.status_code, 200)

    def test_manager_dashboard_access(self):
        self.client.login(username='manager1', password='pass123')
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)
