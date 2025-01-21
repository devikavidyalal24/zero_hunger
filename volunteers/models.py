from django.db import models
from users.models import CustomUser
from donations.models import Donation

class VolunteerTask(models.Model):
    TASK_TYPE_CHOICES = [
        ('collection', 'Collection'),
        ('preparation', 'Meal Preparation'),
        ('distribution', 'Distribution'),
    ]

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    volunteers_needed = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='volunteer_tasks', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_volunteer = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')

    def __str__(self):
        return f"{self.title} - {self.date}"

    def create_notification(self):
        if self.assigned_volunteer:
            TaskNotification.objects.create(
                volunteer=self.assigned_volunteer,
                task=self,
                notification_type='assignment',
                message=f"You have been assigned a new {self.get_task_type_display()} task at {self.location} scheduled for {self.date} at {self.start_time}"
            )
    
    def save(self, *args, **kwargs):
        is_new_assignment = False
        if self.pk:
            old_task = VolunteerTask.objects.get(pk=self.pk)
            if old_task.assigned_volunteer != self.assigned_volunteer and self.assigned_volunteer:
                is_new_assignment = True
        else:
            if self.assigned_volunteer:
                is_new_assignment = True
                
        super().save(*args, **kwargs)
        
        if is_new_assignment:
            self.create_notification()

class TaskAssignment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    task = models.ForeignKey(VolunteerTask, on_delete=models.CASCADE, related_name='assignments')
    volunteer = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='task_assignments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    rating = models.PositiveIntegerField(null=True, blank=True, choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ['task', 'volunteer']

    def __str__(self):
        return f"{self.volunteer.username} - {self.task.title}"

    def save(self, *args, **kwargs):
        if self.status == 'accepted' and not self.task.assigned_volunteer:
            self.task.assigned_volunteer = self.volunteer
            self.task.status = 'assigned'
            self.task.save()
        super().save(*args, **kwargs)

class VolunteerAvailability(models.Model):
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
        ('sunday', 'Sunday'),
    ]

    volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='availabilities')
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)

    class Meta:
        unique_together = ['volunteer', 'day']
        verbose_name_plural = 'Volunteer availabilities'

    def __str__(self):
        return f"{self.volunteer.username} - {self.day}"

class TaskNotification(models.Model):
    TYPE_CHOICES = [
        ('assignment', 'New Assignment'),
        ('reminder', 'Task Reminder'),
        ('update', 'Task Update'),
        ('completion', 'Task Completion'),
        ('feedback', 'Feedback Request'),
    ]

    volunteer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='task_notifications')
    task = models.ForeignKey(VolunteerTask, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.notification_type} for {self.volunteer.username}"

    class Meta:
        ordering = ['-created_at']
