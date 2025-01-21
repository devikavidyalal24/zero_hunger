from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import VolunteerTask, TaskAssignment, VolunteerAvailability, TaskNotification
from nonprofits.models import DonationManagement
from users.models import CustomUser
from notifications.utils import create_notification
from donations.models import Donation
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.middleware.csrf import get_token
from .forms import DeliveryFeedbackForm

def is_volunteer(user):
    return user.is_authenticated and user.role == 'volunteer' and user.is_approved

@login_required
@user_passes_test(is_volunteer)
def dashboard(request):
    # Get task type filter from request
    task_type = request.GET.get('task_type', '')
    
    # Get assigned donations with proper filtering
    assigned_donations = DonationManagement.objects.filter(
        assigned_volunteer=request.user,
        status__in=['pickup_scheduled', 'in_transit']
    ).select_related('donation')
    
    # Get assigned tasks with filtering
    assigned_tasks = VolunteerTask.objects.filter(
        assigned_volunteer=request.user
    )
    
    if task_type:
        assigned_tasks = assigned_tasks.filter(task_type=task_type)
    
    # Get notifications
    notifications = TaskNotification.objects.filter(
        volunteer=request.user,
        is_read=False
    ).order_by('-created_at')[:5]
    
    context = {
        'assigned_donations': assigned_donations,
        'assigned_tasks': assigned_tasks,
        'notifications': notifications,
        'task_types': VolunteerTask.TASK_TYPE_CHOICES,
        'selected_type': task_type
    }
    return render(request, 'volunteers/dashboard.html', context)

@login_required
@user_passes_test(is_volunteer)
def task_list(request):
    available_tasks = VolunteerTask.objects.filter(status='open')
    return render(request, 'volunteers/task_list.html', {'tasks': available_tasks})

@login_required
@user_passes_test(is_volunteer)
def task_detail(request, task_id):
    task = get_object_or_404(VolunteerTask, id=task_id)
    assignment = TaskAssignment.objects.filter(task=task, volunteer=request.user).first()
    
    if request.method == 'POST':
        if 'signup' in request.POST:
            TaskAssignment.objects.create(
                task=task,
                volunteer=request.user,
                status='pending'
            )
            messages.success(request, 'You have successfully signed up for this task!')
            return redirect('volunteers:dashboard')
            
    context = {
        'task': task,
        'assignment': assignment,
    }
    return render(request, 'volunteers/task_detail.html', context)

@login_required
@user_passes_test(is_volunteer)
def my_tasks(request):
    task_type = request.GET.get('task_type', '')
    
    assignments = TaskAssignment.objects.filter(
        volunteer=request.user
    ).select_related('task')
    
    if task_type:
        assignments = assignments.filter(task__task_type=task_type)
    
    context = {
        'assignments': assignments,
        'task_type': task_type,
        'TASK_TYPE_CHOICES': VolunteerTask.TASK_TYPE_CHOICES
    }
    return render(request, 'volunteers/my_tasks.html', {'assignments': assignments})

@login_required
@user_passes_test(is_volunteer)
def update_task_status(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, id=assignment_id, volunteer=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['accepted', 'declined', 'completed']:
            assignment.status = new_status
            if new_status == 'completed':
                assignment.completed_at = timezone.now()
            assignment.save()
            messages.success(request, f'Task status updated to {new_status}!')
            
    return redirect('volunteers:my_tasks')

@login_required
@user_passes_test(is_volunteer)
def submit_feedback(request, assignment_id):
    assignment = get_object_or_404(TaskAssignment, id=assignment_id, volunteer=request.user)
    
    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('volunteers:my_tasks')
    else:
        form = TaskAssignmentForm(instance=assignment)
    
    return render(request, 'volunteers/submit_feedback.html', {
        'form': form,
        'assignment': assignment
    })

@login_required
@user_passes_test(is_volunteer)
def manage_availability(request):
    availabilities = VolunteerAvailability.objects.filter(volunteer=request.user)
    
    if request.method == 'POST':
        form = VolunteerAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.volunteer = request.user
            availability.save()
            messages.success(request, 'Availability updated successfully!')
            return redirect('volunteers:manage_availability')
    else:
        form = VolunteerAvailabilityForm()
    
    return render(request, 'volunteers/manage_availability.html', {
        'form': form,
        'availabilities': availabilities
    })

@login_required
@user_passes_test(is_volunteer)
def notifications(request):
    notifications = TaskNotification.objects.filter(
        volunteer=request.user
    ).order_by('-created_at')
    
    return render(request, 'volunteers/notifications.html', {
        'notifications': notifications
    })

@login_required
@user_passes_test(is_volunteer)
@require_POST
def mark_all_notifications_read(request):
    TaskNotification.objects.filter(
        volunteer=request.user,
        is_read=False
    ).update(is_read=True)
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_volunteer)
@require_POST
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        TaskNotification,
        id=notification_id,
        volunteer=request.user
    )
    notification.is_read = True
    notification.save()
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(is_volunteer)
def complete_pickup(request, management_id):
    management = get_object_or_404(
        DonationManagement, 
        id=management_id,
        assigned_volunteer=request.user
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'picked_up':
            management.status = 'in_transit'
            management.donation.status = 'picked_up'
            management.save()
            management.donation.save()
            
            # Create notification for nonprofit
            create_notification(
                recipient=CustomUser.objects.filter(role='non_profit').first(),
                title="Donation Picked Up",
                message=f"Donation {management.donation.food_name} has been picked up by {request.user.username}",
                notification_type='donation_update'
            )
            
            messages.success(request, 'Donation marked as picked up successfully!')
            return redirect('volunteers:dashboard')
            
        elif action == 'delivered':
            form = DeliveryFeedbackForm(request.POST)
            if form.is_valid():
                management.status = 'received'
                management.donation.status = 'delivered'
                management.received_at = timezone.now()
                management.received_by = request.user
                
                # Update donation with feedback
                management.donation.beneficiaries_reached = form.cleaned_data['beneficiaries_reached']
                management.donation.notes = form.cleaned_data['food_feedback']
                
                management.save()
                management.donation.save()
                
                # Create notification for donor with feedback details in message
                donation_url = f"/donations/detail/{management.donation.id}/"
                create_notification(
                    recipient=management.donation.donor,
                    title="Donation Delivered - Feedback Available",
                    message=f"Your donation of {management.donation.food_name} has been delivered! "
                           f"Beneficiaries reached: {form.cleaned_data['beneficiaries_reached']}. "
                           f"View full details at: {donation_url}",
                    notification_type='donation_update'
                )
                
                messages.success(request, 'Donation marked as delivered and feedback submitted successfully!')
                return redirect('volunteers:dashboard')
            else:
                # If form is invalid, render it again
                return render(request, 'volunteers/delivery_feedback.html', {
                    'form': form,
                    'management': management
                })
        
        # If action is 'delivered' but no POST data (first click)
        if action == 'delivered':
            form = DeliveryFeedbackForm()
            return render(request, 'volunteers/delivery_feedback.html', {
                'form': form,
                'management': management
            })
            
    return redirect('volunteers:dashboard')

def assign_task(request, task_id):
    task = get_object_or_404(VolunteerTask, id=task_id)
    if request.method == 'POST':
        volunteer_id = request.POST.get('volunteer_id')
        volunteer = get_object_or_404(CustomUser, id=volunteer_id)
        task.volunteer = volunteer
        task.status = 'assigned'
        task.save()
        
        # Notify volunteer about task assignment
        notify_task_assignment(task, volunteer)
        return redirect('volunteers:task_detail', task_id=task.id)
