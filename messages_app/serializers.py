from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    time_ago = serializers.SerializerMethodField()

    def get_time_ago(self, obj):
        from django.utils import timezone
        diff = timezone.now() - obj.sent_at
        if diff.days > 0:
            return f"{diff.days}d ago"
        hours = diff.seconds // 3600
        if hours > 0:
            return f"{hours}h ago"
        minutes = diff.seconds // 60
        return f"{minutes}m ago"

    class Meta:
        model = Message
        fields = '__all__'