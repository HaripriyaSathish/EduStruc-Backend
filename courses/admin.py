from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ['course_code', 'course_name', 'instructor', 'status', 'department']
    list_filter   = ['status', 'department']
    search_fields = ['course_name', 'instructor', 'course_code']