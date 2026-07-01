# support_tickets/models.py

from django.db import models
from django.conf import settings


class SupportTicket(models.Model):
    CATEGORY_CHOICES = [
        ('Technical Issue',  'Technical Issue'),
        ('Account Access',   'Account Access'),
        ('Data & Reports',   'Data & Reports'),
        ('Feature Request',  'Feature Request'),
        ('Billing',          'Billing'),
        ('Other',            'Other'),
    ]
    PRIORITY_CHOICES = [
        ('Low',      'Low'),
        ('Medium',   'Medium'),
        ('High',     'High'),
        ('Critical', 'Critical'),
    ]
    STATUS_CHOICES = [
        ('open',        'Open'),
        ('in_progress', 'In Progress'),
        ('resolved',    'Resolved'),
    ]

    raised_by       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject         = models.CharField(max_length=200)
    category        = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Technical Issue')
    priority        = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    message         = models.TextField()
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='open')
    admin_response  = models.TextField(blank=True)
    responded_by    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='ticket_responses')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)
    resolved_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} ({self.raised_by.email}) - {self.status}'