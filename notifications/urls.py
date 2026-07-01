# notifications/urls.py  (create this new file)

from django.urls import path
from . import views

urlpatterns = [
    path('',               views.list_notifications, name='list-notifications'),
    path('<int:pk>/read/', views.mark_read,           name='mark-read'),
    path('read-all/',      views.mark_all_read,       name='mark-all-read'),
]


# ─────────────────────────────────────────────────────────────
# notifications/admin.py  (so you can manually add test notifications
# via Django admin while testing)

# from django.contrib import admin
# from .models import Notification
#
# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('title', 'user', 'type', 'is_read', 'created_at')
#     list_filter  = ('type', 'is_read')


# ─────────────────────────────────────────────────────────────
# edustruc/settings.py — add 'notifications' to INSTALLED_APPS,
# right after 'payments':
#
# INSTALLED_APPS = [
#     ...
#     'payments',
#     'notifications',
# ]


# ─────────────────────────────────────────────────────────────
# edustruc/urls.py — add this line wherever your other
# api/... includes are (e.g. next to api/students/, api/courses/):
#
# path('api/notifications/', include('notifications.urls')),