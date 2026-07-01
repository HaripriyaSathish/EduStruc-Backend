from django.db import models
from django.conf import settings

class Message(models.Model):
    CATEGORY_CHOICES = [
        ('teacher', 'Teacher'),
        ('newsletter', 'Newsletter'),
        ('coach', 'Coach'),
        ('admin', 'Admin'),
    ]
    sender_name = models.CharField(max_length=100)
    sender_role = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='teacher')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    is_read = models.BooleanField(default=False)
    is_urgent = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    attachment_name = models.CharField(max_length=200, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.sender_name} → {self.recipient.email}: {self.subject}"