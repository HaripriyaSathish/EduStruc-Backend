from rest_framework import serializers
from .models import StudentInsight

class StudentInsightSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInsight
        fields = '__all__'