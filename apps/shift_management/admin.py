from django.contrib import admin
from .models import Store, Shift, ShiftVolunteer, ShiftHistory


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'state', 'manager', 'is_active', 'created_at']
    list_filter = ['is_active', 'state', 'city']
    search_fields = ['name', 'city', 'address']
    ordering = ['name']


@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ['title', 'store', 'manager', 'shift_date', 'start_time', 'status', 'slots_available']
    list_filter = ['status', 'role_required', 'shift_date']
    search_fields = ['title', 'description', 'store__name']
    ordering = ['-shift_date']


@admin.register(ShiftVolunteer)
class ShiftVolunteerAdmin(admin.ModelAdmin):
    list_display = ['volunteer', 'shift', 'status', 'applied_at', 'reviewed_by']
    list_filter = ['status', 'applied_at']
    search_fields = ['volunteer__username', 'shift__title']
    ordering = ['-applied_at']


@admin.register(ShiftHistory)
class ShiftHistoryAdmin(admin.ModelAdmin):
    list_display = ['shift', 'action', 'performed_by', 'timestamp']
    list_filter = ['action', 'timestamp']
    search_fields = ['shift__title', 'description']
    readonly_fields = ['shift', 'action', 'performed_by', 'description', 'timestamp']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        return False
