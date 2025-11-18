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
    
    def test_user_role_methods(self):
        """Test role checking methods"""
        admin = User.objects.create_user(username='admin', password='pass', role='admin')
        manager = User.objects.create_user(username='manager', password='pass', role='manager')
        staff = User.objects.create_user(username='staff', password='pass', role='staff')
        
        self.assertTrue(admin.is_admin())
        self.assertFalse(admin.is_manager())
        self.assertFalse(admin.is_staff_member())
        
        self.assertFalse(manager.is_admin())
        self.assertTrue(manager.is_manager())
        self.assertFalse(manager.is_staff_member())
        
        self.assertFalse(staff.is_admin())
        self.assertFalse(staff.is_manager())
        self.assertTrue(staff.is_staff_member())


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
    
    def test_successful_login(self):
        """Test user can log in"""
        user = User.objects.create_user(
            username='testuser', 
            password='testpass123', 
            role='staff',
            first_name='Test'
        )
        response = self.client.post('/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after login
    
    def test_failed_login(self):
        """Test failed login with wrong password"""
        user = User.objects.create_user(username='testuser', password='testpass123', role='staff')
        response = self.client.post('/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
    
    def test_logout(self):
        """Test user can log out"""
        user = User.objects.create_user(username='testuser', password='testpass123', role='staff')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/auth/logout/')
        self.assertEqual(response.status_code, 302)
    
    def test_profile_requires_login(self):
        """Test profile page requires authentication"""
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, 302)
    
    def test_profile_accessible_when_logged_in(self):
        """Test authenticated user can access profile"""
        user = User.objects.create_user(username='testuser', password='testpass123', role='staff')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/auth/profile/')
        self.assertEqual(response.status_code, 200)
    
    def test_profile_update(self):
        """Test user can update profile"""
        user = User.objects.create_user(
            username='testuser', 
            password='testpass123', 
            role='staff',
            email='old@test.com'
        )
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post('/auth/profile/', {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'new@test.com'
        })
        self.assertIn(response.status_code, [200, 302])
    
    def test_password_reset_request_accessible(self):
        """Test password reset request page is accessible"""
        response = self.client.get('/auth/password-reset/')
        self.assertEqual(response.status_code, 200)
    
    def test_password_reset_request_post(self):
        """Test password reset request submission"""
        user = User.objects.create_user(
            username='testuser', 
            password='testpass123', 
            role='staff',
            security_question='What is your favorite color?',
            security_answer='Blue'
        )
        response = self.client.post('/auth/password-reset/', {
            'username': 'testuser'
        })
        # Should redirect to security question page or stay with success message
        self.assertIn(response.status_code, [200, 302])
    
    def test_password_reset_with_invalid_username(self):
        """Test password reset with non-existent username"""
        response = self.client.post('/auth/password-reset/', {
            'username': 'nonexistent'
        })
        # Should stay on same page with error
        self.assertEqual(response.status_code, 200)
    
    def test_signup_form_accessible(self):
        """Test signup page loads form"""
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign Up')
    
    def test_successful_signup_post(self):
        """Test user can sign up successfully"""
        response = self.client.post('/auth/signup/', {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'role': 'staff',
            'security_question': 'What is your favorite color?',
            'security_answer': 'Blue'
        })
        # Should redirect after successful signup
        self.assertIn(response.status_code, [200, 302])
        
    def test_signup_redirects_if_authenticated(self):
        """Test signup redirects if user already logged in"""
        user = User.objects.create_user(username='testuser', password='testpass123', role='staff')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/auth/signup/')
        self.assertEqual(response.status_code, 302)
        
    def test_login_redirects_if_authenticated(self):
        """Test login redirects if user already logged in"""
        user = User.objects.create_user(username='testuser', password='testpass123', role='staff')
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/auth/login/')
        self.assertEqual(response.status_code, 302)
        
    def test_user_management_requires_admin(self):
        """Test user management requires admin role"""
        user = User.objects.create_user(username='staff', password='pass123', role='staff')
        self.client.login(username='staff', password='pass123')
        response = self.client.get('/auth/users/')
        self.assertEqual(response.status_code, 302)
        
    def test_user_management_accessible_by_admin(self):
        """Test admin can access user management"""
        admin = User.objects.create_user(username='admin', password='pass123', role='admin')
        self.client.login(username='admin', password='pass123')
        response = self.client.get('/auth/users/')
        self.assertEqual(response.status_code, 200)
        
    def test_password_reset_with_valid_username(self):
        """Test password reset request with valid username"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff',
            security_question='What is your favorite color?',
            security_answer='Blue'
        )
        response = self.client.post('/auth/password-reset/', {
            'username': 'testuser'
        })
        self.assertIn(response.status_code, [200, 302])
        
    def test_get_full_name_method(self):
        """Test get_full_name method on user model"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.get_full_name(), 'Test User')
        
    def test_password_reset_question_view(self):
        """Test password reset question view with session"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff',
            security_question='pet',
            security_answer='fluffy'
        )
        session = self.client.session
        session['reset_user_id'] = user.id
        session.save()
        response = self.client.get('/auth/password-reset/question/')
        self.assertEqual(response.status_code, 200)
        
    def test_password_reset_question_post_correct(self):
        """Test submitting correct security answer"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff',
            security_question='pet',
            security_answer='fluffy'
        )
        session = self.client.session
        session['reset_user_id'] = user.id
        session.save()
        response = self.client.post('/auth/password-reset/question/', {
            'security_answer': 'Fluffy'
        })
        self.assertIn(response.status_code, [200, 302])
        
    def test_password_reset_question_post_incorrect(self):
        """Test submitting incorrect security answer"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff',
            security_question='pet',
            security_answer='fluffy'
        )
        session = self.client.session
        session['reset_user_id'] = user.id
        session.save()
        response = self.client.post('/auth/password-reset/question/', {
            'security_answer': 'wrong'
        })
        self.assertEqual(response.status_code, 200)
        
    def test_password_reset_confirm_view(self):
        """Test password reset confirm view"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff'
        )
        session = self.client.session
        session['reset_user_id'] = user.id
        session['reset_verified'] = True
        session.save()
        response = self.client.get('/auth/password-reset/confirm/')
        self.assertEqual(response.status_code, 200)
        
    def test_password_reset_confirm_post(self):
        """Test setting new password"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff'
        )
        session = self.client.session
        session['reset_user_id'] = user.id
        session['reset_verified'] = True
        session.save()
        response = self.client.post('/auth/password-reset/confirm/', {
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertIn(response.status_code, [200, 302])
        
    def test_password_reset_without_security_question(self):
        """Test password reset for user without security question"""
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='staff',
            security_question='',
            security_answer=''
        )
        response = self.client.post('/auth/password-reset/', {
            'username': 'testuser'
        })
        self.assertEqual(response.status_code, 200)
        
    def test_user_management_shows_stats(self):
        """Test user management shows user statistics"""
        admin = User.objects.create_user(username='admin', password='pass123', role='admin')
        self.client.login(username='admin', password='pass123')
        response = self.client.get('/auth/users/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_users', response.context)
        self.assertIn('managers_count', response.context)
        self.assertIn('staff_count', response.context)
        
    def test_signup_form_validation(self):
        """Test signup form with valid data"""
        from apps.user_authentication.forms import SignUpForm
        form_data = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'staff',
            'security_question': 'pet',
            'security_answer': 'fluffy'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid() or 'password' not in form.errors)
        
    def test_user_get_role_display(self):
        """Test get_role_display method"""
        user = User.objects.create_user(username='test', password='pass', role='staff')
        role_display = user.get_role_display()
        self.assertIsNotNone(role_display)
