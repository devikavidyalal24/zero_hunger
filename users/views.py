from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import DonorRegistrationForm, VolunteerRegistrationForm, NonProfitRegistrationForm, CustomLoginForm, ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm
from .models import CustomUser, RegistrationRequest
from django.utils import timezone
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from notifications.utils import create_notification
from django.core.cache import cache
from .utils import generate_otp, send_otp_email


def home(request):
    return render(request, 'home.html')

    
def is_admin(user):
    return user.role == 'admin'

def donor_register(request):
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            RegistrationRequest.objects.create(user=user)
            messages.success(request, 'Registration submitted successfully. Please wait for admin approval.')
            return redirect('login')
    else:
        form = DonorRegistrationForm()
    return render(request, 'users/register.html', {'form': form, 'role': 'Donor'})

def volunteer_register(request):
    if request.method == 'POST':
        form = VolunteerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            RegistrationRequest.objects.create(user=user)
            messages.success(request, 'Registration submitted successfully. Please wait for admin approval.')
            return redirect('login')
    else:
        form = VolunteerRegistrationForm()
    return render(request, 'users/register.html', {'form': form, 'role': 'Volunteer'})

def nonprofit_register(request):
    if request.method == 'POST':
        form = NonProfitRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            RegistrationRequest.objects.create(user=user)
            messages.success(request, 'Registration submitted successfully. Please wait for admin approval.')
            return redirect('login')
    else:
        form = NonProfitRegistrationForm()
    return render(request, 'users/register.html', {'form': form, 'role': 'Non-Profit'})

@login_required
@user_passes_test(is_admin)
def pending_requests(request):
    requests = RegistrationRequest.objects.filter(approved_at__isnull=True)
    return render(request, 'users/pending_requests.html', {'requests': requests})

@login_required
@user_passes_test(is_admin)
def approve_request(request, request_id):
    reg_request = RegistrationRequest.objects.get(id=request_id)
    user = reg_request.user
    user.is_approved = True
    user.save()
    
    reg_request.approved_at = timezone.now()
    reg_request.approved_by = request.user
    reg_request.save()
    
    messages.success(request, f'User {user.username} has been approved.')
    return redirect('pending_requests')

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomLoginForm
    
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_approved and user.role != 'admin':
            messages.error(self.request, 'Your account is pending approval.')
            return self.form_invalid(form)
            
        # Add role-based redirect logic
        if user.is_authenticated:
            if user.role == 'donor':
                self.success_url = '/donations/history/'
            elif user.role == 'non_profit':
                self.success_url = '/nonprofits/dashboard/'
            elif user.role == 'volunteer':
                self.success_url = '/volunteers/dashboard/'
            elif user.role == 'admin':
                self.success_url = '/admin-panel/'
                
        return super().form_valid(form)

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

def home_view(request):
    return render(request, 'users/home.html')

@login_required
@never_cache
def custom_logout(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    response = redirect('login')
    # Clear browser cache and prevent back button
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Create notification for admin
            admin_users = CustomUser.objects.filter(is_superuser=True)
            for admin in admin_users:
                create_notification(
                    recipient=admin,
                    title="New User Registration",
                    message=f"New user {user.username} has registered as {user.get_role_display()}",
                    notification_type='admin_alert'
                )
            return redirect('login')

def login_success(request):
    """
    Redirects users based on their role after login
    """
    if request.user.is_authenticated:
        if request.user.role == 'donor':
            return redirect('donations:donation_history')
        elif request.user.role == 'non_profit':
            return redirect('nonprofits:dashboard')
        elif request.user.role == 'volunteer':
            return redirect('volunteers:dashboard')
        elif request.user.role == 'admin':
            return redirect('admin_panel:dashboard')
    return redirect('home')

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            
            try:
                user = CustomUser.objects.get(username=username, email=email)
                otp = generate_otp()
                
                # Store OTP in cache with 10 minutes expiry
                cache_key = f"pwd_reset_otp_{username}"
                cache.set(cache_key, otp, timeout=600)
                
                # Send OTP via email
                if send_otp_email(email, otp):
                    request.session['reset_username'] = username
                    messages.success(request, 'OTP has been sent to your email.')
                    return redirect('verify_otp')
                else:
                    messages.error(request, 'Error sending OTP. Please try again.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid username or email.')
    else:
        form = ForgotPasswordForm()
    
    return render(request, 'users/forgot_password.html', {'form': form})

def verify_otp(request):
    username = request.session.get('reset_username')
    if not username:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            cache_key = f"pwd_reset_otp_{username}"
            stored_otp = cache.get(cache_key)
            
            if stored_otp and stored_otp == entered_otp:
                return redirect('reset_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerificationForm()
    
    return render(request, 'users/verify_otp.html', {'form': form})

def reset_password(request):
    username = request.session.get('reset_username')
    if not username:
        return redirect('forgot_password')
    
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            try:
                user = CustomUser.objects.get(username=username)
                user.set_password(form.cleaned_data['new_password'])
                user.save()
                
                # Clear session and cache
                del request.session['reset_username']
                cache.delete(f"pwd_reset_otp_{username}")
                
                messages.success(request, 'Password reset successful. Please login with your new password.')
                return redirect('login')
            except CustomUser.DoesNotExist:
                messages.error(request, 'User not found.')
    else:
        form = ResetPasswordForm()
    
    return render(request, 'users/reset_password.html', {'form': form})
