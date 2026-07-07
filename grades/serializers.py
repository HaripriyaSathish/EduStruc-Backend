from rest_framework import serializers
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    roll_number  = serializers.CharField(source='student.roll_number', read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'roll_number', 'course',
            'score', 'max_score', 'grade_letter', 'assessment_type',
            'assessment_name', 'date', 'remarks',
        ]