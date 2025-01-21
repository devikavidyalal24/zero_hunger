from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'volunteers'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('complete-pickup/<int:management_id>/', views.complete_pickup, name='complete_pickup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('my-tasks/', views.my_tasks, name='my_tasks'),
    path('task/<int:assignment_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
] 