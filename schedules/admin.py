from django.contrib import admin
from .models import Schedule

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display  = ['course_name', 'instructor', 'day', 'start_time', 'room']
    search_fields = ['course_name', 'instructor']
