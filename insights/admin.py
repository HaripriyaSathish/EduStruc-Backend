from django.contrib import admin
from .models import StudentInsight

@admin.register(StudentInsight)
class StudentInsightAdmin(admin.ModelAdmin):
    list_display = ['student', 'class_rank', 'updated_at']