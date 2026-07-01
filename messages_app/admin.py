from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender_name', 'subject', 'recipient', 'is_read', 'is_urgent', 'is_archived', 'sent_at']
    list_filter = ['category', 'is_read', 'is_urgent', 'is_archived']
    search_fields = ['sender_name', 'subject', 'body']