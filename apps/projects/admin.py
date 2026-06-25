from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'updated_at', 'created_at']
    list_filter = ['owner']
    search_fields = ['name', 'owner__username']
    ordering = ['-updated_at']
    readonly_fields = ['id', 'created_at', 'updated_at']
