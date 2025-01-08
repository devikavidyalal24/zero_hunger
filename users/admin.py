from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, RegistrationRequest
from django.utils import timezone

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'date_joined')
    list_filter = ('role', 'is_approved')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    actions = ['approve_users', 'reject_users']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Approval Status', {'fields': ('is_approved', 'role')}),
    )

    def approve_users(self, request, queryset):
        queryset.update(is_approved=True)
        # Update corresponding registration requests
        for user in queryset:
            RegistrationRequest.objects.filter(user=user).update(
                approved_at=timezone.now(),
                approved_by=request.user
            )
    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        queryset.update(is_approved=False)
    reject_users.short_description = "Reject selected users"

class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_role', 'created_at', 'approved_at', 'approved_by', 'status')
    list_filter = ('approved_at', 'user__role')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    actions = ['approve_requests', 'reject_requests']
    
    def user_role(self, obj):
        return obj.user.get_role_display()
    user_role.short_description = 'Role'

    def status(self, obj):
        return "Approved" if obj.approved_at else "Pending"
    status.short_description = 'Status'

    def approve_requests(self, request, queryset):
        for reg_request in queryset:
            reg_request.approved_at = timezone.now()
            reg_request.approved_by = request.user
            reg_request.save()
            
            # Update user approval status
            user = reg_request.user
            user.is_approved = True
            user.save()
    approve_requests.short_description = "Approve selected requests"

    def reject_requests(self, request, queryset):
        queryset.update(approved_at=None, approved_by=None)
        # Update user approval status
        for reg_request in queryset:
            reg_request.user.is_approved = False
            reg_request.user.save()
    reject_requests.short_description = "Reject selected requests"

    def has_add_permission(self, request):
        return False

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(RegistrationRequest, RegistrationRequestAdmin)
