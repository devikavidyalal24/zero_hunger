from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('users/deactivate/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('donations/', views.donation_monitoring, name='donation_monitoring'),
    path('reports/', views.reports, name='reports'),
    path('notifications/', views.notification_management, name='notification_management'),
] 