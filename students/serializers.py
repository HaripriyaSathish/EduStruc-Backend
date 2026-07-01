from rest_framework import serializers
from .models import Student

class StudentSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = Student
        fields = '__all__'

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None
    

avatar_url = serializers.SerializerMethodField()

def get_avatar_url(self, obj):
    request = self.context.get('request')
    if obj.avatar and request:
        return request.build_absolute_uri(obj.avatar.url)
    return None    