from django.db import models

class Course(models.Model):
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('completed', 'Completed')]

    course_code   = models.CharField(max_length=20, unique=True)
    course_name   = models.CharField(max_length=200)
    description   = models.TextField(blank=True)
    instructor    = models.CharField(max_length=100)  # kept for backward compatibility
    credits       = models.IntegerField(default=3)
    max_students  = models.IntegerField(default=40)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    academic_year = models.CharField(max_length=50)
    semester      = models.CharField(max_length=200)
    department    = models.CharField(max_length=200, blank=True)
    created_at    = models.DateTimeField(auto_now_add=True)

    # New — optional real links, all nullable so existing courses are unaffected
    teacher = models.ForeignKey(
        'teachers.TeacherProfile', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses'
    )
    subject = models.ForeignKey(
        'teachers.Subject', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses'
    )
    grade = models.ForeignKey(
        'teachers.Grade', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='courses'
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"