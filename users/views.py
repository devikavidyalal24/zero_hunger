from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .forms import DonorRegistrationForm, VolunteerRegistrationForm, NonProfitRegistrationForm, CustomLoginForm
from .models import CustomUser, RegistrationRequest
from django.utils import timezone
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache


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
