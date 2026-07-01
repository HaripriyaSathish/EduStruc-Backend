from rest_framework import serializers
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    percentage = serializers.SerializerMethodField()

    def get_percentage(self, obj):
        return round((obj.score / obj.max_score) * 100, 1)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'course', 'course_name',
            'score', 'max_score', 'percentage', 'grade_letter',
            'assessment_type', 'assessment_name', 'date', 'remarks'
        ]