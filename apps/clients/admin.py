from django.contrib import admin

from clients.models import ClientProfile

# Register your models here.

@admin.register(ClientProfile)
class UserProfile(admin.ModelAdmin):
    list_display = ['client', 'phone_number', 'address', 'date_of_birth']
    search_fields = ['client', 'phone_number', 'address', 'date_of_birth']
    ordering = ['client']
    filter_horizontal = [] # This is used to display many-to-many fields in a horizontal manner.
