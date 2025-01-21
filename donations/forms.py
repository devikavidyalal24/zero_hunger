from django import forms
from .models import Donation
from django.utils import timezone

class DonationForm(forms.ModelForm):
    pickup_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        help_text='Select a date for pickup'
    )
    pickup_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text='Select a time for pickup'
    )

    class Meta:
        model = Donation
        fields = ['food_name', 'quantity', 'pickup_location', 'pickup_date', 'pickup_time']
        widgets = {
            'food_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter food name'
            }),
            'pickup_location': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Enter the pickup address'
            }),
        }
