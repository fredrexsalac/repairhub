from django.contrib import admin

from .models import AdminUser, Appointment


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'full_name', 'created_at')
    search_fields = ('username', 'full_name')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('appointment_id', 'full_name', 'device_type', 'service_type', 'status', 'preferred_datetime')
    list_filter = ('device_type', 'status', 'location', 'created_at')
    search_fields = ('appointment_id', 'full_name', 'contact_number', 'brand_model')
    readonly_fields = ('appointment_id', 'created_at', 'updated_at')
