from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import SignUpForm, LoginForm, PasswordResetRequestForm, SecurityQuestionForm, SetNewPasswordForm, SECURITY_QUESTIONS
from .models import CustomUser, AuditLog

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def log_audit(user, action, description, request, details=None):
    """Helper function to log audit events"""
    AuditLog.objects.create(
        user=user,
        action=action,
        description=description,
        ip_address=get_client_ip(request),
        details=details
    )

def signup_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_audit(user, 'create_user', f'New user registered: {user.username}', request)
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = SignUpForm()
    
    return render(request, 'user_authentication/signup.html', {'form': form})

def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                log_audit(user, 'login', f'User logged in: {user.username}', request)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'user_authentication/login.html', {'form': form})

@login_required
def logout_view(request):
    """User logout view"""
    user = request.user
    log_audit(user, 'logout', f'User logged out: {user.username}', request)
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

def password_reset_request(request):
    """Step 1: Request password reset by username"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = CustomUser.objects.get(username=username)
                if user.security_question:
                    request.session['reset_user_id'] = user.id
                    return redirect('password_reset_question')
                else:
                    messages.error(request, 'No security question set for this account.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Username not found.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'user_authentication/password_reset_request.html', {'form': form})

def password_reset_question(request):
    """Step 2: Answer security question"""
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('password_reset_request')
    
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid session.')
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            answer = form.cleaned_data['security_answer'].lower().strip()
            if answer == user.security_answer:
                request.session['reset_verified'] = True
                return redirect('password_reset_confirm')
            else:
                messages.error(request, 'Incorrect answer. Please try again.')
    else:
        form = SecurityQuestionForm()
    
    question_dict = dict(SECURITY_QUESTIONS)
    return render(request, 'user_authentication/password_reset_question.html', {
        'form': form,
        'security_question': question_dict.get(user.security_question, '')
    })

def password_reset_confirm(request):
    """Step 3: Set new password"""
    if not request.session.get('reset_verified'):
        return redirect('password_reset_request')
    
    user_id = request.session.get('reset_user_id')
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Invalid session.')
        return redirect('password_reset_request')
    
    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            log_audit(user, 'update_user', f'Password reset for user: {user.username}', request)
            
            # Clear session
            del request.session['reset_user_id']
            del request.session['reset_verified']
            
            messages.success(request, 'Password reset successfully! Please login with your new password.')
            return redirect('login')
    else:
        form = SetNewPasswordForm()
    
    return render(request, 'user_authentication/password_reset_confirm.html', {'form': form})

@login_required
def profile_view(request):
    """User profile view"""
    return render(request, 'user_authentication/profile.html', {'user': request.user})
