from django.db import models
from users.models import CustomUser
from django.utils import timezone

class Donation(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('picked_up', 'Picked Up'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='donations')
    food_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(help_text="Number of servings/portions")
    pickup_location = models.TextField()
    pickup_date = models.DateField()
    pickup_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    beneficiaries_reached = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.donor.username}'s donation - {self.food_name} ({self.status})"
