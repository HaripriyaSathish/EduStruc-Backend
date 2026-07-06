from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = Student
        fields = '__all__'

    def get_avatar_url(self, obj):
        if obj.avatar_base64:
            return obj.avatar_base64
        return None