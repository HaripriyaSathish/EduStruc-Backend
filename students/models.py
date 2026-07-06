from django.db import models
from django.conf import settings

class Student(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('graduated', 'Graduated')]
    roll_number   = models.CharField(max_length=20, unique=True)
    full_name     = models.CharField(max_length=100)
    email         = models.EmailField(unique=True)
    phone         = models.CharField(max_length=15, blank=True)
    gender        = models.CharField(max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True, blank=True)
    class_name    = models.CharField(max_length=50)
    section       = models.CharField(max_length=10, blank=True)
    academic_year = models.CharField(max_length=20)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    address       = models.TextField(blank=True)
    avatar_base64 = models.TextField(blank=True, null=True)
    parent_name   = models.CharField(max_length=100, blank=True)
    parent_phone  = models.CharField(max_length=15, blank=True)

    parent        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='children',
        limit_choices_to={'role': 'parent'}
    )
    created_at    = models.DateTimeField(auto_now_add=True)
    updated_at    = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.roll_number} - {self.full_name}"