from django.db import models
from students.models import Student

class StudentInsight(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='insight')
    academic_insight = models.TextField(blank=True)
    performance_strengths = models.JSONField(default=list)
    class_rank = models.CharField(max_length=50, blank=True)
    medical_alerts = models.JSONField(default=list, help_text='[{"title": "Nut Allergy", "detail": "Carries EpiPen"}]')
    emergency_contacts = models.JSONField(default=list, help_text='[{"name": "Sarah", "relation": "Mother (Primary)", "phone": "1234567890", "is_primary": true}]')
    extracurriculars = models.JSONField(default=list, help_text='["Honors Program", "Varsity Soccer"]')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Insight for {self.student.full_name}"