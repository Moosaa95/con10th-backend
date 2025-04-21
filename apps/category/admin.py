from django.contrib import admin
from .models import Category, Skill

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'is_predefined', 'requested_by', 'created_at')
    search_fields = ('name',)
    list_filter = ('status', 'is_predefined')
    ordering = ('-created_at',)
    list_per_page = 10

# @admin.register(Skill)
# class SkillAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'status', 'is_predefined', 'requested_by', 'created_at')
#     search_fields = ('name',)
#     list_filter = ('status', 'is_predefined')
#     ordering = ('-created_at',)
#     list_per_page = 10


