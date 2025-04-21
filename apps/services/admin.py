from django.contrib import admin
from .models import  Service, ServiceRequest
# Register your models here.


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ['service', 'status', 'created_at']
    search_fields = ['service__name', 'status']
    ordering = ['created_at']
    list_filter = ['status']