from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import TeacherProfile, TeacherTimetable


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_teacher_profile(sender, instance, created, **kwargs):
    if instance.role == 'teacher':
        TeacherProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=TeacherTimetable)
def sync_schedule_from_timetable(sender, instance, created, **kwargs):
    """
    Reverse sync: if a TeacherTimetable entry is created or edited directly
    (e.g. via Django admin) without going through the Schedule form, this
    automatically creates/updates a matching Schedule row so it also shows
    up on the Schedule calendar in both Admin and Teacher Portal.
    """
    from schedules.models import Schedule

    if instance.source_schedule_id:
        # Already linked — just keep the existing Schedule row updated
        Schedule.objects.filter(id=instance.source_schedule_id).update(
            course_name=instance.subject.name if instance.subject else 'Untitled',
            instructor=instance.teacher.user.full_name,
            day=instance.day,
            start_time=instance.start_time,
            end_time=instance.end_time,
            room=instance.room,
            teacher=instance.teacher,
            subject=instance.subject,
            grade=instance.grade,
        )
        return

    # No linked schedule yet — create one and link it back
    schedule = Schedule.objects.create(
        course_name=instance.subject.name if instance.subject else 'Untitled',
        instructor=instance.teacher.user.full_name,
        day=instance.day,
        start_time=instance.start_time,
        end_time=instance.end_time,
        room=instance.room,
        academic_year='2025-2026',
        semester='Current Term',
        teacher=instance.teacher,
        subject=instance.subject,
        grade=instance.grade,
    )

    TeacherTimetable.objects.filter(pk=instance.pk).update(source_schedule=schedule)