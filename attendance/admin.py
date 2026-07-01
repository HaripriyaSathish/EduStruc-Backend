from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'event_name']
    list_filter = ['status', 'date']
    search_fields = ['student__full_name', 'event_name']