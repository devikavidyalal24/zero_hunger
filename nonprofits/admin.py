from django.contrib import admin
from .models import DonationManagement, FoodInventory, DistributionPlan, DistributionRecord

@admin.register(DonationManagement)
class DonationManagementAdmin(admin.ModelAdmin):
    list_display = ('donation', 'status', 'scheduled_pickup_time', 'assigned_volunteer', 'received_at')
    list_filter = ('status', 'scheduled_pickup_time', 'received_at')
    search_fields = ('donation__food_name', 'nonprofit_notes')
    raw_id_fields = ('donation', 'assigned_volunteer', 'received_by')

@admin.register(FoodInventory)
class FoodInventoryAdmin(admin.ModelAdmin):
    list_display = ('donation_management', 'received_quantity', 'available_quantity', 
                   'storage_type', 'expiry_date', 'quality_check_passed')
    list_filter = ('storage_type', 'quality_check_passed', 'expiry_date')
    search_fields = ('storage_location', 'quality_notes')

@admin.register(DistributionPlan)
class DistributionPlanAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'distribution_date', 'planned_quantity', 
                   'estimated_beneficiaries', 'status')
    list_filter = ('status', 'distribution_date')
    search_fields = ('location_name', 'location_address', 'notes')
    raw_id_fields = ('inventory', 'coordinator')

@admin.register(DistributionRecord)
class DistributionRecordAdmin(admin.ModelAdmin):
    list_display = ('distribution_plan', 'actual_quantity_distributed', 
                   'actual_beneficiaries_served', 'distribution_start_time')
    search_fields = ('feedback', 'challenges_faced')
    raw_id_fields = ('distribution_plan', 'created_by')
