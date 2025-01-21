from django.contrib import admin
from .models import Donation
from django.db.models import Count, Sum
from django.utils.html import format_html

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'food_name', 'quantity', 'status', 'pickup_date', 'created_at')
    list_filter = ('status', 'pickup_date', 'created_at')
    search_fields = ('donor__username', 'food_name', 'pickup_location')
    readonly_fields = ('donor', 'food_name', 'quantity', 'status', 'pickup_date', 'pickup_time', 
                      'pickup_location', 'created_at')
    
    def has_add_permission(self, request):
        return False  # Admin cannot add donations
    
    def has_change_permission(self, request, obj=None):
        return False  # Admin cannot modify donations
    
    def has_delete_permission(self, request, obj=None):
        return False  # Admin cannot delete donations

    def changelist_view(self, request, extra_context=None):
        # Add summary statistics to the change list view
        extra_context = extra_context or {}
        
        # Get queryset
        queryset = self.get_queryset(request)
        
        # Calculate statistics
        stats = {
            'total_donations': queryset.count(),
            'total_quantity': queryset.aggregate(Sum('quantity'))['quantity__sum'] or 0,
            'by_status': queryset.values('status').annotate(count=Count('id')),
        }
        
        extra_context['donation_stats'] = stats
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
