from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('donor', 'Donor'),
        ('volunteer', 'Volunteer'),
        ('non_profit', 'Non Profit'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    is_approved = models.BooleanField(default=False)
    
    # Additional fields based on role
    organization_name = models.CharField(max_length=255, blank=True, null=True)  # For non-profits
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

class RegistrationRequest(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='approved_requests')
