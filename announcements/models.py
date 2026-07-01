from django.db import models

class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('all', 'All'),
        ('parents', 'Parents Only'),
        ('teachers', 'Teachers Only'),
    ]
    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    event_date = models.DateTimeField(null=True, blank=True)
    event_location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']