from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from donations.models import Donation
from .models import DonationManagement, FoodInventory, DistributionPlan, DistributionRecord
from .forms import (DonationManagementForm, FoodInventoryForm, 
                   DistributionPlanForm, DistributionRecordForm)
from volunteers.models import VolunteerTask, TaskAssignment
from volunteers.forms import VolunteerTaskForm
from notifications.utils import create_notification

def is_nonprofit(user):
    return user.is_authenticated and user.role == 'non_profit' and user.is_approved

@login_required
@user_passes_test(is_nonprofit)
def dashboard(request):
    # Get all donations that don't have management yet
    unmanaged_donations = Donation.objects.filter(
        status='delivered',
        nonprofit_management__isnull=True
    )
    
    # Get all managed donations
    managed_donations = DonationManagement.objects.all()
    
    active_distributions = DistributionPlan.objects.filter(
        status__in=['planned', 'in_progress']
    ).select_related('inventory__donation_management__donation')
    
    low_inventory = FoodInventory.objects.filter(
        available_quantity__lt=10
    ).select_related('donation_management__donation')
    
    context = {
        'pending_donations': unmanaged_donations,
        'managed_donations': managed_donations,
        'active_distributions': active_distributions,
        'low_inventory': low_inventory,
    }
    return render(request, 'nonprofits/dashboard.html', context)

@login_required
@user_passes_test(is_nonprofit)
def donation_management_list(request):
    # Get all donations that don't have management yet
    unmanaged_donations = Donation.objects.filter(
        nonprofit_management__isnull=True
    )
    
    # Get all managed donations
    managed_donations = DonationManagement.objects.all().select_related('donation')
    
    context = {
        'unmanaged_donations': unmanaged_donations,
        'managed_donations': managed_donations,
    }
    return render(request, 'nonprofits/donation_management_list.html', context)

@login_required
@user_passes_test(is_nonprofit)
def manage_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    donation_management, created = DonationManagement.objects.get_or_create(
        donation=donation,
        defaults={'status': 'pending_review'}
    )
    
    if request.method == 'POST':
        form = DonationManagementForm(request.POST, instance=donation_management)
        if form.is_valid():
            management = form.save()
            
            # Create or update volunteer task
            if management.assigned_volunteer:
                task_type = form.cleaned_data['task_type']
                scheduled_time = form.cleaned_data['scheduled_pickup_time']
                
                # Get the latest task or create new one
                task = VolunteerTask.objects.filter(
                    donation=donation
                ).order_by('-created_at').first()
                
                if not task:
                    task = VolunteerTask.objects.create(
                        donation=donation,
                        title=f"{task_type.title()}: {donation.food_name}",
                        task_type=task_type,
                        description=f"Handle {donation.food_name} donation from {donation.donor.get_full_name()}",
                        location=donation.pickup_location,
                        date=scheduled_time.date(),
                        start_time=scheduled_time.time(),
                        end_time=(scheduled_time + timezone.timedelta(hours=1)).time(),
                        volunteers_needed=1,
                        status='assigned',
                        assigned_volunteer=management.assigned_volunteer
                    )
                else:
                    task.task_type = task_type
                    task.date = scheduled_time.date()
                    task.start_time = scheduled_time.time()
                    task.end_time = (scheduled_time + timezone.timedelta(hours=1)).time()
                    task.assigned_volunteer = management.assigned_volunteer
                    task.save()
                
                TaskAssignment.objects.get_or_create(
                    task=task,
                    volunteer=management.assigned_volunteer,
                    defaults={'status': 'pending'}
                )
                
                # Create notification with both in-app and email
                notification_title = "New Task Assignment"
                notification_message = (
                    f"You have been assigned a new task for donation: {donation.food_name}\n"
                    f"Type: {task_type}\n"
                    f"Location: {donation.pickup_location}\n"
                    f"Date: {scheduled_time.date()}\n"
                    f"Time: {scheduled_time.time()}\n"
                    f"Donor: {donation.donor.get_full_name()}"
                )
                
                create_notification(
                    recipient=management.assigned_volunteer,
                    title=notification_title,
                    message=notification_message,
                    notification_type='task_reminder'
                )
            
            messages.success(request, 'Donation management updated successfully!')
            return redirect('nonprofits:donation_management_list')
    else:
        form = DonationManagementForm(instance=donation_management)
    
    return render(request, 'nonprofits/manage_donation.html', {
        'form': form,
        'donation': donation,
        'management': donation_management
    })

@login_required
@user_passes_test(is_nonprofit)
def inventory_list(request):
    inventory_items = FoodInventory.objects.all().select_related(
        'donation_management__donation')
    return render(request, 'nonprofits/inventory_list.html', 
                 {'inventory_items': inventory_items})

@login_required
@user_passes_test(is_nonprofit)
def add_to_inventory(request, management_id):
    donation_management = get_object_or_404(DonationManagement, id=management_id)
    
    if request.method == 'POST':
        form = FoodInventoryForm(request.POST)
        if form.is_valid():
            inventory = form.save(commit=False)
            inventory.donation_management = donation_management
            inventory.save()
            messages.success(request, 'Added to inventory successfully!')
            return redirect('nonprofits:inventory_list')
    else:
        form = FoodInventoryForm()
    
    return render(request, 'nonprofits/add_to_inventory.html', {
        'form': form,
        'donation': donation_management
    })

@login_required
@user_passes_test(is_nonprofit)
def distribution_list(request):
    distributions = DistributionPlan.objects.all().select_related(
        'inventory__donation_management__donation')
    return render(request, 'nonprofits/distribution_list.html',
                 {'distributions': distributions})

@login_required
@user_passes_test(is_nonprofit)
def create_distribution(request, inventory_id):
    inventory = get_object_or_404(FoodInventory, id=inventory_id)
    
    if request.method == 'POST':
        form = DistributionPlanForm(request.POST)
        if form.is_valid():
            distribution = form.save(commit=False)
            distribution.inventory = inventory
            distribution.coordinator = request.user
            distribution.save()
            
            messages.success(request, 'Distribution planned successfully!')
            return redirect('nonprofits:distribution_list')
    else:
        form = DistributionPlanForm()
    
    return render(request, 'nonprofits/create_distribution.html',
                 {'form': form, 'inventory': inventory})

@login_required
@user_passes_test(is_nonprofit)
def record_distribution(request, distribution_id):
    distribution = get_object_or_404(DistributionPlan, id=distribution_id)
    
    if request.method == 'POST':
        form = DistributionRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.distribution_plan = distribution
            record.created_by = request.user
            record.save()
            
            # Update inventory
            inventory = distribution.inventory
            inventory.available_quantity -= record.actual_quantity_distributed
            inventory.save()
            
            # Update distribution status
            distribution.status = 'completed'
            distribution.save()
            
            messages.success(request, 'Distribution recorded successfully!')
            return redirect('nonprofits:distribution_list')
    else:
        form = DistributionRecordForm()
    
    return render(request, 'nonprofits/record_distribution.html',
                 {'form': form, 'distribution': distribution})

@login_required
@user_passes_test(is_nonprofit)
def create_volunteer_task(request):
    if request.method == 'POST':
        form = VolunteerTaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Volunteer task created successfully!')
            return redirect('nonprofits:manage_volunteer_tasks')
    else:
        form = VolunteerTaskForm()
    
    return render(request, 'nonprofits/create_volunteer_task.html', {'form': form})

@login_required
@user_passes_test(is_nonprofit)
def manage_volunteer_tasks(request):
    tasks = VolunteerTask.objects.all()
    return render(request, 'nonprofits/manage_volunteer_tasks.html', {'tasks': tasks})

@login_required
@user_passes_test(is_nonprofit)
def accept_donation(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    if request.method == 'POST':
        donation.status = 'accepted'
        donation.save()
        
        # Notify donor
        create_notification(
            recipient=donation.donor,
            title="Donation Accepted",
            message=f"Your donation of {donation.food_name} has been accepted by {request.user.organization_name}",
            notification_type='donation_update'
        )
        return redirect('nonprofits:donation_list')

@login_required
@user_passes_test(is_nonprofit)
def update_inventory(request, inventory_id):
    inventory = get_object_or_404(FoodInventory, id=inventory_id)
    
    if request.method == 'POST':
        form = InventoryUpdateForm(request.POST, instance=inventory)
        if form.is_valid():
            inventory = form.save()
            messages.success(request, 'Inventory updated successfully!')
            return redirect('nonprofits:inventory_list')
    else:
        form = InventoryUpdateForm(instance=inventory)
    
    return render(request, 'nonprofits/update_inventory.html', {
        'form': form,
        'inventory': inventory
    })
