from django.db import models
from students.models import Student

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('holiday', 'Holiday'),
        ('upcoming', 'Upcoming'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')
    event_name = models.CharField(max_length=200, help_text="e.g. Science Fair, Regular School Day")
    event_type = models.CharField(max_length=100, blank=True, help_text="e.g. Academic Deadline, Standard Attendance")
    time = models.TimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {self.status}"