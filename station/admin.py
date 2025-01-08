from django.contrib import admin
from station.models import Station_inspection, Station,Vehicle_inspection,Fleet_order

class Station_Admin(admin.ModelAdmin):
    list_display = ['name', 'location']
    search_fields = ['name', 'location']
    list_filter = ['name', 'location']

class Station_inspection_Admin(admin.ModelAdmin):
    list_display = ['station__id', 'station__name', 'date', 'submitted_by','saved_on']
    search_fields = ['station__id', 'station__name']
    list_filter = ['station__id', 'station__name','date','submitted_by']

class Vehicle_inspection_Admin(admin.ModelAdmin):
    list_display = ['station__id', 'vehicle', 'type', 'technician','date']
    search_fields = ['station__id', 'type']
    list_filter = ['type', 'type','technician']

class Fleet_order_Admin(admin.ModelAdmin):
    list_display = ['station__id','date', 'requested_by', 'submitted_by', 'status','urgency_level','type','saved_on']
    search_fields = ['status', 'urgency_level','requested_by','type','station__id']
    list_filter = ['status', 'urgency_level','status','type','station__id']


admin.site.register(Station,Station_Admin)
admin.site.register(Station_inspection,Station_inspection_Admin)
admin.site.register(Vehicle_inspection,Vehicle_inspection_Admin)
admin.site.register(Fleet_order,Fleet_order_Admin)