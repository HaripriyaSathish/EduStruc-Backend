# support_tickets/serializers.py

from rest_framework import serializers
from .models import SupportTicket


class SupportTicketSerializer(serializers.ModelSerializer):
    raised_by_name  = serializers.CharField(source='raised_by.full_name', read_only=True)
    raised_by_email = serializers.CharField(source='raised_by.email', read_only=True)
    raised_by_role  = serializers.CharField(source='raised_by.role', read_only=True)
    responded_by_name = serializers.CharField(source='responded_by.full_name', read_only=True, default=None)

    class Meta:
        model = SupportTicket
        fields = [
            'id', 'subject', 'category', 'priority', 'message', 'status',
            'admin_response', 'responded_by_name', 'created_at', 'updated_at',
            'resolved_at', 'raised_by_name', 'raised_by_email', 'raised_by_role',
        ]
        read_only_fields = [
            'id', 'status', 'admin_response', 'responded_by_name',
            'created_at', 'updated_at', 'resolved_at',
            'raised_by_name', 'raised_by_email', 'raised_by_role',
        ]