from django.conf import settings
from .models import Notification


def notify_admins(title, message='', type='system', link=None):
    """
    Creates a notification for every admin user. Used to surface real
    system events (enrollments, schedule changes, etc.) in the admin
    Dashboard's Recent Activity feed and notification bell.
    """
    User = settings.AUTH_USER_MODEL
    from django.apps import apps
    UserModel = apps.get_model(User)
    admins = UserModel.objects.filter(role='admin', is_active=True)
    Notification.objects.bulk_create([
        Notification(user=admin, title=title, message=message, type=type, link=link)
        for admin in admins
    ])