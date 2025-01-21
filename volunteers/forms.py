from django import forms
from .models import VolunteerTask, TaskAssignment, VolunteerAvailability

class VolunteerTaskForm(forms.ModelForm):
    class Meta:
        model = VolunteerTask
        fields = ['title', 'task_type', 'description', 'location', 
                 'date', 'start_time', 'end_time', 'volunteers_needed']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class TaskAssignmentForm(forms.ModelForm):
    class Meta:
        model = TaskAssignment
        fields = ['feedback', 'rating']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }

class VolunteerAvailabilityForm(forms.ModelForm):
    class Meta:
        model = VolunteerAvailability
        fields = ['day', 'start_time', 'end_time', 'is_recurring']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class DeliveryFeedbackForm(forms.Form):
    beneficiaries_reached = forms.IntegerField(
        min_value=1,
        label="Number of Beneficiaries Reached",
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    food_feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please provide feedback about the food quality and condition upon delivery'
        }),
        label="Feedback about Food"
    ) 