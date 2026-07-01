from django.contrib import admin
from .models import Announcement

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'audience', 'event_date', 'is_active', 'created_at']
    list_filter = ['audience', 'is_active']