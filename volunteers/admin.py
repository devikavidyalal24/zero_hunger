from django.contrib import admin
from .models import VolunteerTask, TaskAssignment, VolunteerAvailability, TaskNotification

@admin.register(VolunteerTask)
class VolunteerTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task_type', 'date', 'status', 'volunteers_needed')
    list_filter = ('task_type', 'status', 'date')
    search_fields = ('title', 'description', 'location')

@admin.register(TaskAssignment)
class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'task', 'status', 'assigned_at', 'completed_at')
    list_filter = ('status', 'assigned_at', 'completed_at')
    search_fields = ('volunteer__username', 'task__title')

@admin.register(VolunteerAvailability)
class VolunteerAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'day', 'start_time', 'end_time', 'is_recurring')
    list_filter = ('day', 'is_recurring')
    search_fields = ('volunteer__username',)

@admin.register(TaskNotification)
class TaskNotificationAdmin(admin.ModelAdmin):
    list_display = ('volunteer', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('volunteer__username', 'message')
