from django.db import models

class Schedule(models.Model):
    DAY_CHOICES = [
        ('Monday','Monday'),('Tuesday','Tuesday'),('Wednesday','Wednesday'),
        ('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday'),
    ]
    course_name  = models.CharField(max_length=200)
    instructor   = models.CharField(max_length=100)
    day          = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time   = models.TimeField()
    end_time     = models.TimeField()
    room         = models.CharField(max_length=50)
    academic_year= models.CharField(max_length=20)
    semester     = models.CharField(max_length=20)
    created_at   = models.DateTimeField(auto_now_add=True)

    # New — optional real links, all nullable so existing schedules are unaffected
    course = models.ForeignKey(
        'courses.Course', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedule_entries'
    )
    teacher = models.ForeignKey(
        'teachers.TeacherProfile', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedules'
    )
    subject = models.ForeignKey(
        'teachers.Subject', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedules'
    )
    grade = models.ForeignKey(
        'teachers.Grade', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='schedules'
    )

    def __str__(self):
        return f"{self.course_name} - {self.day} {self.start_time}"
    

from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=Schedule)
def notify_schedule_change(sender, instance, created, **kwargs):
    from notifications.utils import notify_admins
    action = 'created' if created else 'updated'
    notify_admins(
        title=f'Schedule {action.capitalize()}: {instance.course_name}',
        message=f'{instance.day} {instance.start_time}–{instance.end_time} in {instance.room or "TBD"}',
        type='schedule',
        link='/schedules',
    )    