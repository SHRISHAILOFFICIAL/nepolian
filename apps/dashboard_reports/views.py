from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse
from apps.user_authentication.models import CustomUser, AuditLog
from apps.shift_management.models import Shift, ShiftVolunteer, Store
from apps.notifications.models import Notification
import csv


@login_required
def dashboard_view(request):
    """Main dashboard - role-specific content"""
    user = request.user
    
    context = {
        'user': user,
        'unread_notifications': Notification.objects.filter(recipient=user, is_read=False).count()
    }
    
    if user.is_staff_member():
        context['available_shifts'] = Shift.objects.filter(
            status='open', shift_date__gte=timezone.now().date()
        ).count()
        context['my_applications'] = ShiftVolunteer.objects.filter(volunteer=user).count()
        context['approved_shifts'] = ShiftVolunteer.objects.filter(
            volunteer=user, status='approved'
        ).count()
    elif user.is_manager() or user.is_admin():
        context['total_shifts'] = Shift.objects.filter(manager=user).count() if user.is_manager() else Shift.objects.count()
        context['open_shifts'] = Shift.objects.filter(status='open').count()
        context['pending_applications'] = ShiftVolunteer.objects.filter(
            shift__manager=user if user.is_manager() else Q(), status='pending'
        ).count() if user.is_manager() else ShiftVolunteer.objects.filter(status='pending').count()
        context['total_staff'] = CustomUser.objects.filter(role='staff').count()
        context['total_stores'] = Store.objects.filter(is_active=True).count()
        context['recent_shifts'] = Shift.objects.select_related('store', 'manager').order_by('-created_at')[:5]
        context['recent_applications'] = ShiftVolunteer.objects.select_related('shift', 'volunteer').order_by('-applied_at')[:5]
    
    return render(request, 'dashboard_reports/dashboard.html', context)


@login_required
def reports_view(request):
    """Reports page for admins and managers"""
    if not (request.user.is_admin() or request.user.is_manager()):
        return render(request, 'dashboard_reports/access_denied.html')
    
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    shifts_query = Shift.objects.all()
    if date_from:
        shifts_query = shifts_query.filter(shift_date__gte=date_from)
    if date_to:
        shifts_query = shifts_query.filter(shift_date__lte=date_to)
    
    stats = {
        'total_shifts': shifts_query.count(),
        'open_shifts': shifts_query.filter(status='open').count(),
        'filled_shifts': shifts_query.filter(status='filled').count(),
        'cancelled_shifts': shifts_query.filter(status='cancelled').count(),
        'total_applications': ShiftVolunteer.objects.count(),
        'approved_applications': ShiftVolunteer.objects.filter(status='approved').count(),
        'rejected_applications': ShiftVolunteer.objects.filter(status='rejected').count(),
        'pending_applications': ShiftVolunteer.objects.filter(status='pending').count(),
    }
    
    top_volunteers = CustomUser.objects.filter(role='staff').annotate(
        approved_count=Count('shift_applications', filter=Q(shift_applications__status='approved'))
    ).order_by('-approved_count')[:10]
    
    context = {'stats': stats, 'top_volunteers': top_volunteers, 'date_from': date_from, 'date_to': date_to}
    return render(request, 'dashboard_reports/reports.html', context)


@login_required
def export_shifts_csv(request):
    """Export shifts to CSV"""
    if not (request.user.is_admin() or request.user.is_manager()):
        return HttpResponse('Unauthorized', status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="shifts_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Title', 'Store', 'Manager', 'Date', 'Start Time', 'End Time', 'Role', 'Slots', 'Status', 'Created At'])
    
    shifts = Shift.objects.select_related('store', 'manager').all()
    for shift in shifts:
        writer.writerow([shift.title, shift.store.name, shift.manager.username, shift.shift_date,
                        shift.start_time, shift.end_time, shift.get_role_required_display(),
                        shift.slots_available, shift.get_status_display(), 
                        shift.created_at.strftime('%Y-%m-%d %H:%M:%S')])
    
    return response


@login_required
def export_volunteers_csv(request):
    """Export volunteer applications to CSV"""
    if not (request.user.is_admin() or request.user.is_manager()):
        return HttpResponse('Unauthorized', status=403)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="volunteers_report.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Volunteer', 'Email', 'Shift', 'Store', 'Date', 'Status', 'Applied At', 'Reviewed By', 'Reviewed At'])
    
    applications = ShiftVolunteer.objects.select_related('volunteer', 'shift', 'shift__store', 'reviewed_by').all()
    for app in applications:
        writer.writerow([app.volunteer.get_full_name(), app.volunteer.email, app.shift.title,
                        app.shift.store.name, app.shift.shift_date, app.get_status_display(),
                        app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                        app.reviewed_by.username if app.reviewed_by else 'N/A',
                        app.reviewed_at.strftime('%Y-%m-%d %H:%M:%S') if app.reviewed_at else 'N/A'])
    
    return response


@login_required
def audit_log_view(request):
    """View audit logs (admin only)"""
    if not request.user.is_admin():
        return render(request, 'dashboard_reports/access_denied.html')
    
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:100]
    return render(request, 'dashboard_reports/audit_log.html', {'logs': logs})
