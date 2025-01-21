from django.db import models
from donations.models import Donation
from users.models import CustomUser
from volunteers.models import VolunteerTask
from django.utils import timezone

class DonationManagement(models.Model):
    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('accepted', 'Accepted by Nonprofit'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('in_transit', 'In Transit'),
        ('received', 'Received at Nonprofit'),
        ('rejected', 'Rejected'),
    ]

    donation = models.OneToOneField(Donation, on_delete=models.CASCADE, related_name='nonprofit_management')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending_review')
    nonprofit_notes = models.TextField(blank=True, null=True, help_text="Internal notes about this donation")
    scheduled_pickup_time = models.DateTimeField(null=True, blank=True)
    assigned_volunteer = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'role': 'volunteer'},
        related_name='assigned_pickups'
    )
    received_at = models.DateTimeField(null=True, blank=True)
    received_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='received_donations'
    )

    def __str__(self):
        return f"Management of {self.donation.food_name} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        create_task = False
        if self.assigned_volunteer and not hasattr(self, 'volunteer_task'):
            create_task = True
        
        super().save(*args, **kwargs)
        
        if create_task:
            # Create volunteer task when volunteer is assigned
            VolunteerTask.objects.create(
                title=f"Pickup: {self.donation.food_name}",
                task_type='pickup',
                description=f"Pickup donation from {self.donation.donor.get_full_name()} at {self.donation.pickup_location}",
                location=self.donation.pickup_location,
                date=self.scheduled_pickup_time.date(),
                start_time=self.scheduled_pickup_time.time(),
                end_time=(self.scheduled_pickup_time + timezone.timedelta(hours=1)).time(),
                volunteers_needed=1,
                status='assigned',
                donation=self.donation
            )

class FoodInventory(models.Model):
    STORAGE_TYPE_CHOICES = [
        ('refrigerated', 'Refrigerated'),
        ('frozen', 'Frozen'),
        ('dry', 'Dry Storage'),
        ('hot', 'Hot Storage'),
    ]

    donation_management = models.OneToOneField(DonationManagement, on_delete=models.CASCADE, related_name='inventory')
    received_quantity = models.PositiveIntegerField()
    available_quantity = models.PositiveIntegerField()
    storage_location = models.CharField(max_length=100)
    storage_type = models.CharField(max_length=20, choices=STORAGE_TYPE_CHOICES)
    expiry_date = models.DateTimeField()
    quality_check_passed = models.BooleanField(default=True)
    quality_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Food Inventories"

    def __str__(self):
        return f"Inventory: {self.donation_management.donation.food_name}"

class DistributionPlan(models.Model):
    STATUS_CHOICES = [
        ('planned', 'Planned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    inventory = models.ForeignKey(FoodInventory, on_delete=models.CASCADE, related_name='distribution_plans')
    location_name = models.CharField(max_length=100)
    location_address = models.TextField()
    distribution_date = models.DateField()
    distribution_time = models.TimeField()
    planned_quantity = models.PositiveIntegerField()
    estimated_beneficiaries = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planned')
    coordinator = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='coordinated_distributions'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Distribution at {self.location_name} on {self.distribution_date}"

class DistributionRecord(models.Model):
    distribution_plan = models.OneToOneField(DistributionPlan, on_delete=models.CASCADE, related_name='record')
    actual_quantity_distributed = models.PositiveIntegerField()
    actual_beneficiaries_served = models.PositiveIntegerField()
    distribution_start_time = models.DateTimeField()
    distribution_end_time = models.DateTimeField()
    feedback = models.TextField(blank=True, null=True)
    challenges_faced = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name='distribution_records'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.distribution_plan}"
