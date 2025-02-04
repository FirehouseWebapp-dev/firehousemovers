from django.contrib import admin
from .models import Crew, Vehicle, AvailabilityData, Dispatch, Order,CrewStaff

# Custom ModelAdmin for AvailabilityData
class AvailabilityDataAdmin(admin.ModelAdmin):
    list_display = ['vehicle', 'status', 'estimated_back_in_service_date', 'back_in_service_date', 'date_saved']
    search_fields = ['vehicle__name', 'vehicle__number']
    list_filter = ['status', 'vehicle__vehicle_type']
    actions = ['delete_selected_records']

    def delete_selected_records(self, request, queryset):
        """
        Custom action for deleting multiple records at once.
        """
        queryset.delete()
        self.message_user(request, "Selected records were successfully deleted.")
    
    delete_selected_records.short_description = "Delete selected records"



class OrderAdmin(admin.ModelAdmin):
    list_display = ['date','job_no', 'last_name_customer', 'type_of_move', 'phone_number']
    search_fields = ['last_name_customer', 'phone_number','date']
    list_filter = ['date', 'phone_number']

class DispatchAdmin(admin.ModelAdmin):
    list_display = ['order__job_no', 'ipad', 'crew_leads', 'order__last_name_customer', 'submitted_by', 'submitted_on']
    search_fields = ['drivers', 'order']
    list_filter = ['crew_leads', 'drivers']

class VehicleAdmin(admin.ModelAdmin):
    list_display = ['name', 'number', 'vehicle_type', 'last_inspection_date']
    search_fields = ['number', 'name']
    list_filter = ['vehicle_type', 'name','number']

class CrewStaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'crew', 'role']
    search_fields = ['name', 'crew','role']
    list_filter = ['crew', 'role']

admin.site.register(Vehicle,VehicleAdmin)
admin.site.register(AvailabilityData, AvailabilityDataAdmin)
admin.site.register(Dispatch, DispatchAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Crew)
admin.site.register(CrewStaff,CrewStaffAdmin)
