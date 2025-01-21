from django import forms
from .models import DonationManagement, FoodInventory, DistributionPlan, DistributionRecord
from users.models import CustomUser
from volunteers.models import VolunteerTask

class DonationManagementForm(forms.ModelForm):
    task_type = forms.ChoiceField(
        choices=VolunteerTask.TASK_TYPE_CHOICES,
        required=True
    )
    
    class Meta:
        model = DonationManagement
        fields = [
            'status',
            'nonprofit_notes',
            'scheduled_pickup_time',
            'assigned_volunteer',
            'task_type'
        ]
        widgets = {
            'nonprofit_notes': forms.Textarea(attrs={'rows': 3}),
            'scheduled_pickup_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_volunteer'].queryset = CustomUser.objects.filter(
            role='volunteer',
            is_approved=True
        )

class FoodInventoryForm(forms.ModelForm):
    class Meta:
        model = FoodInventory
        fields = ['received_quantity', 'available_quantity', 'storage_type', 
                 'storage_location', 'expiry_date', 'quality_notes']
        widgets = {
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        received_qty = cleaned_data.get('received_quantity')
        available_qty = cleaned_data.get('available_quantity')

        if available_qty and received_qty and available_qty > received_qty:
            raise forms.ValidationError("Available quantity cannot be greater than received quantity")
        
        return cleaned_data

class DistributionPlanForm(forms.ModelForm):
    class Meta:
        model = DistributionPlan
        fields = ['location_name', 'location_address', 'distribution_date', 
                 'distribution_time', 'planned_quantity', 'estimated_beneficiaries', 'notes']
        widgets = {
            'distribution_date': forms.DateInput(attrs={'type': 'date'}),
            'distribution_time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DistributionRecordForm(forms.ModelForm):
    class Meta:
        model = DistributionRecord
        fields = ['actual_quantity_distributed', 'actual_beneficiaries_served',
                 'distribution_start_time', 'distribution_end_time', 
                 'feedback', 'challenges_faced']
        widgets = {
            'distribution_start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'distribution_end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'feedback': forms.Textarea(attrs={'rows': 3}),
            'challenges_faced': forms.Textarea(attrs={'rows': 3}),
        } 

class InventoryUpdateForm(forms.ModelForm):
    class Meta:
        model = FoodInventory
        fields = ['available_quantity', 'storage_location', 'quality_notes'] 