from django.db import models
from students.models import Student
from courses.models import Course

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='grades')
    score = models.FloatField()
    max_score = models.FloatField(default=100)
    grade_letter = models.CharField(max_length=5, blank=True)
    assessment_type = models.CharField(max_length=100, help_text="e.g. Quiz, Lab, Essay, Exam")
    assessment_name = models.CharField(max_length=200, help_text="e.g. Calculus Quiz, Biology Lab")
    date = models.DateField()
    remarks = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        percentage = (self.score / self.max_score) * 100
        if percentage >= 90:
            self.grade_letter = 'A'
        elif percentage >= 80:
            self.grade_letter = 'B+'
        elif percentage >= 70:
            self.grade_letter = 'B'
        elif percentage >= 60:
            self.grade_letter = 'C'
        elif percentage >= 50:
            self.grade_letter = 'D'
        else:
            self.grade_letter = 'F'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.full_name} - {self.assessment_name} - {self.grade_letter}"

    class Meta:
        ordering = ['-date']