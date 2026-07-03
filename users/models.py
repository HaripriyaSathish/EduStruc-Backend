from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin',   'Admin'),
        ('teacher', 'Teacher'),
        ('parent',  'Parent'),
    ]
    email            = models.EmailField(unique=True)
    full_name        = models.CharField(max_length=100)
    institution_name = models.CharField(max_length=200, blank=True)
    role             = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
    phone            = models.CharField(max_length=15, blank=True)
    job_title        = models.CharField(max_length=100, blank=True)
    timezone         = models.CharField(max_length=100, blank=True, default='Eastern Standard Time (GMT-5)')
    avatar_base64    = models.TextField(null=True, blank=True)
    two_fa_enabled   = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=True)
    is_staff         = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.email} ({self.role})"
    

    