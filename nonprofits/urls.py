from django.urls import path
from . import views

app_name = 'nonprofits'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('donations/', views.donation_management_list, name='donation_management_list'),
    path('donations/manage/<int:donation_id>/', views.manage_donation, name='manage_donation'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/<int:management_id>/', views.add_to_inventory, name='add_to_inventory'),
    path('distributions/', views.distribution_list, name='distribution_list'),
    path('distributions/create/<int:inventory_id>/', views.create_distribution, name='create_distribution'),
    path('distributions/record/<int:distribution_id>/', views.record_distribution, name='record_distribution'),
    path('volunteer-tasks/create/', views.create_volunteer_task, name='create_volunteer_task'),
    path('volunteer-tasks/', views.manage_volunteer_tasks, name='manage_volunteer_tasks'),
    path('inventory/<int:inventory_id>/update/', views.update_inventory, name='update_inventory'),
    path('inventory/add/<int:donation_id>/', views.add_to_inventory, name='add_to_inventory'),
] 