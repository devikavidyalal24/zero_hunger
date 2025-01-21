from .models import Notification
from users.models import CustomUser
from django.core.mail import send_mail
from django.conf import settings

def create_notification(recipient, title, message, notification_type):
    """
    Create a new notification
    """
    from notifications.models import Notification
    
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type
    )
    
    # Send email notification if it's a task assignment
    if notification_type == 'task_reminder':
        send_task_email(recipient.email, title, message)
    
    return notification

def send_task_email(email, subject, message):
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def notify_donation_status(donation):
    """
    Create notification for donation status change
    """
    create_notification(
        recipient=donation.donor,
        title=f"Donation Status Update",
        message=f"Your donation '{donation.food_name}' status is now {donation.status}",
        notification_type='donation_update'
    )

def notify_task_assignment(task, volunteer):
    """
    Create notification for task assignment
    """
    create_notification(
        recipient=volunteer,
        title=f"New Task Assignment",
        message=f"You have been assigned to {task.title}",
        notification_type='task_reminder'
    ) 