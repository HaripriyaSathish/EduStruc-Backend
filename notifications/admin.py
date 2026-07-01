# notifications/admin.py  (so you can manually add test notifications
# via Django admin while testing)
 
from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'is_read', 'created_at')
    list_filter  = ('type', 'is_read')
 
 