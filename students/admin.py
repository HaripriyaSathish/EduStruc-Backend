from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['roll_number', 'full_name', 'email', 'class_name', 'status']
    list_filter   = ['status', 'class_name']
    search_fields = ['full_name', 'email', 'roll_number']