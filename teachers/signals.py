from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TeacherProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_teacher_profile(sender, instance, created, **kwargs):
    if instance.role == 'teacher':
        TeacherProfile.objects.get_or_create(user=instance)