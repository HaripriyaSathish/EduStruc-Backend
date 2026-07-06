from django.db import models
from django.conf import settings

class Grade(models.Model):
    name  = models.CharField(max_length=20, unique=True)   # e.g. "Kindergarten 1", "Grade 1" ... "Grade 12"
    order = models.PositiveSmallIntegerField(unique=True)  # controls sort order: KG1=0, KG2=1, Grade 1=2 ...

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class TeacherProfile(models.Model):
    user        = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                        related_name='teacher_profile', limit_choices_to={'role': 'teacher'})
    employee_id = models.CharField(max_length=30, blank=True)
    department  = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True, help_text="e.g. Senior Teacher, HOD")
    date_joined = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.full_name


class TeacherSubjectGrade(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='subject_grades')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade   = models.ForeignKey(Grade, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'subject', 'grade')

    def __str__(self):
        return f"{self.teacher.user.full_name} - {self.subject.name} ({self.grade.name})"


class TeacherAttendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent',  'Absent'),
        ('leave',   'On Leave'),
        ('holiday', 'Holiday'),
    ]
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='attendance')
    date    = models.DateField()
    status  = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    notes   = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('teacher', 'date')

    def __str__(self):
        return f"{self.teacher.user.full_name} - {self.date} - {self.status}"


class TeacherTimetable(models.Model):
    DAY_CHOICES = [
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'),
    ]
    teacher    = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='timetable')
    subject    = models.ForeignKey(Subject, on_delete=models.CASCADE)
    grade      = models.ForeignKey(Grade, on_delete=models.CASCADE)
    day        = models.CharField(max_length=20, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time   = models.TimeField()
    room       = models.CharField(max_length=50, blank=True)
    source_schedule = models.OneToOneField(
        'schedules.Schedule', on_delete=models.CASCADE,
        null=True, blank=True, related_name='timetable_entry',
        help_text="Auto-managed link back to the Schedule entry that generated this row."
    )
    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.teacher.user.full_name} - {self.subject.name} - {self.grade.name} - {self.day}"