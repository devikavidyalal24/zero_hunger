from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser
from donations.models import Donation
from nonprofits.models import DonationManagement, FoodInventory, DistributionPlan, DistributionRecord
from volunteers.models import TaskAssignment, VolunteerTask
from notifications.models import Notification
from notifications.utils import create_notification

def is_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    # Get key metrics
    total_users = CustomUser.objects.count()
    pending_approvals = CustomUser.objects.filter(is_approved=False).count()
    total_donations = Donation.objects.count()
    active_donations = Donation.objects.filter(status__in=['pending', 'accepted']).count()
    
    # Recent activities
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_donations = Donation.objects.order_by('-created_at')[:5]
    
    # Add notification metrics
    total_notifications = Notification.objects.count()
    unread_notifications = Notification.objects.filter(is_read=False).count()
    recent_notifications = Notification.objects.order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'pending_approvals': pending_approvals,
        'total_donations': total_donations,
        'active_donations': active_donations,
        'recent_users': recent_users,
        'recent_donations': recent_donations,
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/user_management.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def approve_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    
    # Notify user about approval
    create_notification(
        recipient=user,
        title="Account Approved",
        message="Your account has been approved. You can now log in and use the platform.",
        notification_type='general'
    )
    messages.success(request, f'User {user.username} has been approved.')
    return redirect('admin_panel:user_management')

@login_required
@user_passes_test(is_admin)
def deactivate_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = False
    user.save()
    messages.success(request, f'User {user.username} has been deactivated.')
    return redirect('admin_panel:user_management')

@login_required
@user_passes_test(is_admin)
def donation_monitoring(request):
    donations = Donation.objects.all().select_related('donor').order_by('-created_at')
    return render(request, 'admin_panel/donation_monitoring.html', {'donations': donations})

@login_required
@user_passes_test(is_admin)
def reports(request):
    # Time-based filters
    today = timezone.now().date()
    thirty_days_ago = today - timedelta(days=30)
    
    # User Statistics
    total_volunteers = CustomUser.objects.filter(role='volunteer', is_approved=True).count()
    active_volunteers = CustomUser.objects.filter(
        role='volunteer',
        is_approved=True,
        assigned_tasks__created_at__gte=thirty_days_ago
    ).distinct().count()
    
    total_donors = CustomUser.objects.filter(role='donor', is_approved=True).count()
    active_donors = CustomUser.objects.filter(
        role='donor',
        donations__created_at__gte=thirty_days_ago
    ).distinct().count()
    
    total_nonprofits = CustomUser.objects.filter(role='non_profit', is_approved=True).count()
    
    # Donation Statistics
    total_donations = Donation.objects.count()
    recent_donations = Donation.objects.filter(created_at__date__gte=thirty_days_ago).count()
    completed_donations = Donation.objects.filter(status='delivered').count()
    
    # Calculate total beneficiaries reached
    total_beneficiaries = Donation.objects.filter(
        status='delivered'
    ).aggregate(
        total=Sum('beneficiaries_reached')
    )['total'] or 0
    
    recent_beneficiaries = Donation.objects.filter(
        status='delivered',
        created_at__date__gte=thirty_days_ago
    ).aggregate(
        total=Sum('beneficiaries_reached')
    )['total'] or 0
    
    # Task Statistics
    total_tasks = VolunteerTask.objects.count()
    completed_tasks = VolunteerTask.objects.filter(status='completed').count()
    
    # Distribution Statistics
    total_distributions = DistributionPlan.objects.count()
    completed_distributions = DistributionPlan.objects.filter(status='completed').count()
    
    # Monthly donation trends
    monthly_donations = Donation.objects.filter(
        created_at__date__gte=thirty_days_ago
    ).count()
    
    # Status-based donation counts
    donation_status_counts = Donation.objects.values('status').annotate(
        count=Count('id')
    )
    
    # Location-based statistics
    top_donation_locations = Donation.objects.values('pickup_location').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    context = {
        'user_stats': {
            'total_volunteers': total_volunteers,
            'active_volunteers': active_volunteers,
            'total_donors': total_donors,
            'active_donors': active_donors,
            'total_nonprofits': total_nonprofits,
        },
        'donation_stats': {
            'total_donations': total_donations,
            'recent_donations': recent_donations,
            'completed_donations': completed_donations,
            'monthly_donations': monthly_donations,
            'status_counts': donation_status_counts,
        },
        'impact_stats': {
            'total_beneficiaries': total_beneficiaries,
            'recent_beneficiaries': recent_beneficiaries,
            'completed_distributions': completed_distributions,
        },
        'task_stats': {
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 2),
        },
        'location_stats': top_donation_locations,
    }
    
    return render(request, 'admin_panel/reports.html', context)

@login_required
@user_passes_test(is_admin)
def notification_management(request):
    # Add print statement for debugging
    notifications = Notification.objects.all().order_by('-created_at')
    print(f"Number of notifications found: {notifications.count()}")
    return render(request, 'admin_panel/notification_management.html', {
        'notifications': notifications
    })
