from rest_framework import serializers
from .models import Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True, default=None)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    grade_name   = serializers.CharField(source='grade.name', read_only=True, default=None)
    course_title = serializers.CharField(source='course.course_name', read_only=True, default=None)

    class Meta:
        model  = Schedule
        fields = [
            'id', 'course_name', 'instructor', 'day', 'start_time', 'end_time',
            'room', 'academic_year', 'semester', 'created_at',
            'course', 'teacher', 'subject', 'grade',
            'teacher_name', 'subject_name', 'grade_name', 'course_title',
        ]