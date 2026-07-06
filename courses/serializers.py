from rest_framework import serializers
from .models import Course

class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.user.full_name', read_only=True, default=None)
    subject_name = serializers.CharField(source='subject.name', read_only=True, default=None)
    grade_name   = serializers.CharField(source='grade.name', read_only=True, default=None)

    class Meta:
        model  = Course
        fields = [
            'id', 'course_code', 'course_name', 'description', 'instructor',
            'credits', 'max_students', 'status', 'academic_year', 'semester',
            'department', 'created_at',
            'teacher', 'subject', 'grade',
            'teacher_name', 'subject_name', 'grade_name',
        ]

    def create(self, validated_data):
        course = super().create(validated_data)
        self._sync_instructor_name(course)
        return course

    def update(self, instance, validated_data):
        course = super().update(instance, validated_data)
        self._sync_instructor_name(course)
        return course

    def _sync_instructor_name(self, course):
        # If a real teacher is linked but instructor text wasn't set, keep them in sync
        if course.teacher and not course.instructor:
            course.instructor = course.teacher.user.full_name
            course.save(update_fields=['instructor'])