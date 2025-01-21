from django.db import models
from users.models import CustomUser
from django.urls import reverse

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('donation_update', 'Donation Update'),
        ('task_reminder', 'Task Reminder'),
        ('admin_alert', 'Admin Alert'),
        ('general', 'General Announcement'),
    ]

    recipient = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.notification_type} for {self.recipient.username}"

    def mark_as_read(self):
        self.is_read = True
        self.save()
