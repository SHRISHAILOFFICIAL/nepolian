from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from apps.user_authentication.models import AuditLog
from apps.user_authentication.views import log_audit
from apps.notifications.views import create_notification
from .models import Shift, ShiftVolunteer, Store, ShiftHistory
from .forms import ShiftForm, VolunteerReviewForm, StoreForm


@login_required
def shift_list_view(request):
    """View all open shifts for staff"""
    shifts = Shift.objects.filter(
        status='open',
        shift_date__gte=timezone.now().date()
    ).select_related('store', 'manager')
    
    role_filter = request.GET.get('role')
    if role_filter:
        shifts = shifts.filter(role_required=role_filter)
    
    store_filter = request.GET.get('store')
    if store_filter:
        shifts = shifts.filter(store_id=store_filter)
    
    stores = Store.objects.filter(is_active=True)
    role_choices = Shift.ROLE_CHOICES
    
    return render(request, 'shift_management/shift_list.html', {
        'shifts': shifts,
        'stores': stores,
        'role_choices': role_choices,
    })


@login_required
def my_shifts_view(request):
    """View user's shift applications"""
    applications = ShiftVolunteer.objects.filter(
        volunteer=request.user
    ).select_related('shift', 'shift__store').order_by('-applied_at')
    
    return render(request, 'shift_management/my_shifts.html', {
        'applications': applications
    })


@login_required
def shift_detail_view(request, shift_id):
    """View shift details"""
    shift = get_object_or_404(Shift, id=shift_id)
    user_application = None
    can_volunteer = False
    
    if request.user.is_staff_member():
        try:
            user_application = ShiftVolunteer.objects.get(shift=shift, volunteer=request.user)
        except ShiftVolunteer.DoesNotExist:
            pass
        can_volunteer = shift.can_volunteer(request.user)
    
    return render(request, 'shift_management/shift_detail.html', {
        'shift': shift,
        'user_application': user_application,
        'can_volunteer': can_volunteer,
    })


@login_required
def volunteer_for_shift(request, shift_id):
    """Staff volunteers for a shift"""
    if not request.user.is_staff_member():
        messages.error(request, 'Only staff members can volunteer for shifts.')
        return redirect('shift_list')
    
    shift = get_object_or_404(Shift, id=shift_id)
    
    if not shift.can_volunteer(request.user):
        messages.error(request, 'You cannot volunteer for this shift.')
        return redirect('shift_detail', shift_id=shift_id)
    
    ShiftVolunteer.objects.create(shift=shift, volunteer=request.user)
    
    # Create notification for manager
    create_notification(
        recipient=shift.manager,
        notification_type='shift_application',
        title='New Volunteer Application',
        message=f'{request.user.get_full_name()} applied for "{shift.title}" on {shift.shift_date}',
        link=f'/shifts/manager/'
    )
    
    log_audit(request.user, 'volunteer', f'Volunteered for shift: {shift.title}', request, 
              details={'shift_id': shift.id})
    
    messages.success(request, 'Successfully applied for shift!')
    return redirect('my_shifts')


@login_required
def withdraw_volunteer(request, application_id):
    """Withdraw volunteer application"""
    application = get_object_or_404(ShiftVolunteer, id=application_id, volunteer=request.user)
    
    if application.status != 'pending':
        messages.error(request, 'Cannot withdraw this application.')
        return redirect('my_shifts')
    
    application.status = 'withdrawn'
    application.save()
    log_audit(request.user, 'volunteer', f'Withdrew application for shift: {application.shift.title}', 
              request, details={'application_id': application.id})
    
    messages.success(request, 'Application withdrawn successfully.')
    return redirect('my_shifts')


@login_required
def manager_dashboard(request):
    """Manager dashboard showing their shifts"""
    if not (request.user.is_manager() or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    shifts = Shift.objects.filter(manager=request.user).select_related('store').prefetch_related('volunteers')
    pending_applications = ShiftVolunteer.objects.filter(
        shift__manager=request.user,
        status='pending'
    ).select_related('shift', 'volunteer').order_by('-applied_at')
    
    # Add volunteer counts to shifts
    for shift in shifts:
        shift.approved_count = shift.volunteers.filter(status='approved').count()
    
    return render(request, 'shift_management/manager_dashboard.html', {
        'shifts': shifts,
        'pending_applications': pending_applications,
    })


@login_required
def create_shift(request):
    """Managers create new shifts"""
    if not (request.user.is_manager() or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.manager = request.user
            shift.save()
            
            ShiftHistory.objects.create(
                shift=shift, action='created', performed_by=request.user,
                description=f'Shift created: {shift.title}'
            )
            log_audit(request.user, 'create_shift', f'Created shift: {shift.title}', request,
                     details={'shift_id': shift.id})
            
            messages.success(request, 'Shift created successfully!')
            return redirect('manager_dashboard')
    else:
        form = ShiftForm()
    
    return render(request, 'shift_management/shift_form.html', {'form': form, 'title': 'Create Shift'})


@login_required
def update_shift(request, shift_id):
    """Managers update existing shifts"""
    shift = get_object_or_404(Shift, id=shift_id)
    
    if not (request.user == shift.manager or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('manager_dashboard')
    
    if request.method == 'POST':
        form = ShiftForm(request.POST, instance=shift)
        if form.is_valid():
            shift = form.save()
            ShiftHistory.objects.create(
                shift=shift, action='updated', performed_by=request.user,
                description=f'Shift updated: {shift.title}'
            )
            log_audit(request.user, 'update_shift', f'Updated shift: {shift.title}', request,
                     details={'shift_id': shift.id})
            
            messages.success(request, 'Shift updated successfully!')
            return redirect('manager_dashboard')
    else:
        form = ShiftForm(instance=shift)
    
    return render(request, 'shift_management/shift_form.html', {
        'form': form, 'title': 'Update Shift', 'shift': shift
    })


@login_required
def cancel_shift(request, shift_id):
    """Managers cancel shifts"""
    shift = get_object_or_404(Shift, id=shift_id)
    
    if not (request.user == shift.manager or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('manager_dashboard')
    
    shift.status = 'cancelled'
    shift.save()
    
    ShiftHistory.objects.create(
        shift=shift, action='cancelled', performed_by=request.user,
        description=f'Shift cancelled: {shift.title}'
    )
    log_audit(request.user, 'delete_shift', f'Cancelled shift: {shift.title}', request,
             details={'shift_id': shift.id})
    
    messages.success(request, 'Shift cancelled successfully.')
    return redirect('manager_dashboard')


@login_required
def review_volunteer(request, application_id):
    """Manager reviews volunteer applications"""
    application = get_object_or_404(ShiftVolunteer, id=application_id)
    
    if not (request.user == application.shift.manager or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('manager_dashboard')
    
    if request.method == 'POST':
        form = VolunteerReviewForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            application.reviewed_by = request.user
            application.reviewed_at = timezone.now()
            application.save()
            
            action = 'approve' if application.status == 'approved' else 'reject'
            log_audit(request.user, action, 
                     f'{action.capitalize()}d volunteer: {application.volunteer.username} for {application.shift.title}',
                     request, details={'application_id': application.id})
            
            messages.success(request, f'Application {application.status} successfully!')
            return redirect('manager_dashboard')
    else:
        form = VolunteerReviewForm(instance=application)
    
    return render(request, 'shift_management/review_volunteer.html', {
        'form': form, 'application': application
    })


@login_required
def approve_volunteer(request, application_id):
    """Quick approve volunteer application"""
    application = get_object_or_404(ShiftVolunteer, id=application_id)
    
    if not (request.user == application.shift.manager or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('manager_dashboard')
    
    application.status = 'approved'
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save()
    
    # Create notification for volunteer
    create_notification(
        recipient=application.volunteer,
        notification_type='application_approved',
        title='Application Approved',
        message=f'Your application for "{application.shift.title}" on {application.shift.shift_date} has been approved!',
        link=f'/shifts/{application.shift.id}/'
    )
    
    log_audit(request.user, 'approve', 
             f'Approved volunteer: {application.volunteer.username} for {application.shift.title}',
             request, details={'application_id': application.id})
    
    messages.success(request, f'Approved {application.volunteer.get_full_name()} for {application.shift.title}!')
    return redirect('manager_dashboard')


@login_required
def reject_volunteer(request, application_id):
    """Quick reject volunteer application"""
    application = get_object_or_404(ShiftVolunteer, id=application_id)
    
    if not (request.user == application.shift.manager or request.user.is_admin()):
        messages.error(request, 'Access denied.')
        return redirect('manager_dashboard')
    
    application.status = 'rejected'
    application.reviewed_by = request.user
    application.reviewed_at = timezone.now()
    application.save()
    
    # Create notification for volunteer
    create_notification(
        recipient=application.volunteer,
        notification_type='application_rejected',
        title='Application Not Approved',
        message=f'Your application for "{application.shift.title}" on {application.shift.shift_date} was not approved.',
        link=f'/shifts/'
    )
    
    log_audit(request.user, 'reject', 
             f'Rejected volunteer: {application.volunteer.username} for {application.shift.title}',
             request, details={'application_id': application.id})
    
    messages.success(request, f'Rejected {application.volunteer.get_full_name()}\'s application.')
    return redirect('manager_dashboard')
