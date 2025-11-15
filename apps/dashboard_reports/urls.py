from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export-shifts/', views.export_shifts_csv, name='export_shifts_csv'),
    path('reports/export-volunteers/', views.export_volunteers_csv, name='export_volunteers_csv'),
    path('audit-logs/', views.audit_log_view, name='audit_logs'),
]
