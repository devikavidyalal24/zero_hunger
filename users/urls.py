from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from users import views

urlpatterns = [
    path('register/donor/', views.donor_register, name='donor_register'),
    path('register/volunteer/', views.volunteer_register, name='volunteer_register'),
    path('register/nonprofit/', views.nonprofit_register, name='nonprofit_register'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('approve-request/<int:request_id>/', views.approve_request, name='approve_request'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.home_view, name='home'),
    path('login-success/', views.login_success, name='login_success'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
] 