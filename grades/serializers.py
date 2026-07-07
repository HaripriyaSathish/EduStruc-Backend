from rest_framework import serializers
from .models import Grade

class GradeSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    roll_number  = serializers.CharField(source='student.roll_number', read_only=True)
    percentage   = serializers.SerializerMethodField()

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'student_name', 'roll_number', 'course',
            'score', 'max_score', 'grade_letter', 'percentage',
            'assessment_type', 'assessment_name', 'date', 'remarks',
        ]

    def get_percentage(self, obj):
        if obj.max_score and obj.max_score > 0:
            return round((obj.score / obj.max_score) * 100)
        return 0