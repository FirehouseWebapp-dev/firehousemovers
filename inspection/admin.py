from django.contrib import admin
from inspection.models import Truck_inspection,Trailer_inspection,Onsite_inspection


class Onsite_inspection_Admin(admin.ModelAdmin):
    list_display = ['job_number','inspector', 'crew_leader', 'customer_name','saved_on']
    search_fields = ['job_number', 'inspector','crew_leader', 'customer_name']
    list_filter = ['inspector', 'crew_leader']


admin.site.register(Truck_inspection)
admin.site.register(Trailer_inspection)
admin.site.register(Onsite_inspection,Onsite_inspection_Admin)