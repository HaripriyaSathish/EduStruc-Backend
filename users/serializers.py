from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = User
        fields = ['full_name', 'institution_name', 'email', 'password', 'role', 'phone']
        extra_kwargs = {
            'role':             {'required': False},
            'phone':            {'required': False},
            'institution_name': {'required': False},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class UserSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'email', 'full_name', 'institution_name', 'role',
                  'phone', 'job_title', 'timezone', 'two_fa_enabled',
                  'avatar_url', 'is_active', 'created_at']

    def get_avatar_url(self, obj):
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None

class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ['full_name', 'email', 'phone', 'job_title',
                  'institution_name', 'timezone', 'two_fa_enabled']
        extra_kwargs = { 'email': {'required': False} }



        