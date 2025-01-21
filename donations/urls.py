from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    path('create/', views.create_donation, name='create_donation'),
    path('history/', views.donation_history, name='donation_history'),
    path('detail/<int:pk>/', views.donation_detail, name='donation_detail'),
    path('donation/<int:donation_id>/impact/', views.view_donation_impact, name='donation_impact'),
]
