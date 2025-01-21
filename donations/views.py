from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Donation
from .forms import DonationForm
from users.models import CustomUser
from notifications.utils import create_notification, notify_donation_status
from django.db.models import Sum

def is_donor(user):
    return user.is_authenticated and user.role == 'donor'

@login_required
@user_passes_test(is_donor)
def create_donation(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = request.user
            donation.save()
            
            # Create notification for admin
            create_notification(
                recipient=CustomUser.objects.filter(is_superuser=True).first(),
                title="New Donation Added",
                message=f"New donation of {donation.food_name} has been added by {request.user.username}",
                notification_type='donation_update'
            )
            return redirect('donations:donation_detail', pk=donation.pk)
    else:
        form = DonationForm()
    return render(request, 'donations/create_donation.html', {'form': form})

@login_required
@user_passes_test(is_donor)
def donation_history(request):
    donations = Donation.objects.filter(donor=request.user)
    return render(request, 'donations/donation_history.html', {'donations': donations})

@login_required
@user_passes_test(is_donor)
def donation_detail(request, pk):
    donation = get_object_or_404(Donation, pk=pk, donor=request.user)
    return render(request, 'donations/donation_detail.html', {'donation': donation})

def update_donation_status(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    if request.method == 'POST':
        # ... your status update logic
        donation.save()
        
        # Notify donor about status change
        notify_donation_status(donation)

@login_required
def view_donation_impact(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id, donor=request.user)
    
    # Get distribution data if exists
    distribution_data = DistributionRecord.objects.filter(
        distribution_plan__inventory__donation_management__donation=donation
    ).aggregate(
        total_beneficiaries=Sum('actual_beneficiaries_served'),
        total_distributed=Sum('actual_quantity_distributed')
    )
    
    context = {
        'donation': donation,
        'impact': distribution_data
    }
    return render(request, 'donations/donation_impact.html', context)
