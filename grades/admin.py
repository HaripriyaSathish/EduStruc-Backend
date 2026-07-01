from django.contrib import admin
from .models import Grade

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment_name', 'score', 'max_score', 'grade_letter', 'date']
    list_filter = ['grade_letter', 'assessment_type']
    search_fields = ['student__full_name', 'assessment_name']