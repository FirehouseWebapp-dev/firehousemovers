from django.db import models
from authentication.models import UserProfile
from vehicle.models import Vehicle



class Station(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


class Station_inspection(models.Model):
    station = models.ForeignKey(Station, related_name="inspections", on_delete=models.CASCADE)

    BACKLOT_CLEANLINESS_CHOICES = [
        ('Clean and orderly', 'Clean and orderly'),
        ('Mostly clean, minor issues', 'Mostly clean, minor issues'),
        ('Needs cleaning', 'Needs cleaning'),
    ]

    MAINTENANCE_CHOICES = [
        ('No maintenance required', 'No maintenance required'),
        ('Minor repairs needed', 'Minor repairs needed'),
        ('Major repairs needed', 'Major repairs needed'),
    ]

    FRONT_CLEANLINESS_CHOICES = [
        ('Clean and presentable', 'Clean and presentable'),
        ('Acceptable', 'Acceptable'),
        ('Needs Attention', 'Needs Attention'),
    ]

    LANDSCAPING_CHOICES = [
        ('Well-maintained', 'Well-maintained'),
        ('Needs minor work', 'Needs minor work'),
        ('Requires significant work', 'Requires significant work'),
    ]

    INVENTORY_CHOICES = [
        ('All tools present', 'All tools present'),
        ('Some tools missing', 'Some tools missing'),
        ('Major inventory issues', 'Major inventory issues'),
    ]

    TOOL_CLEANLINESS_CHOICES = [
        ('Clean and maintained', 'Clean and maintained'),
        ('Mostly clean, some need attention', 'Mostly clean, some need attention'),
        ('Needs thorough cleaning', 'Needs thorough cleaning'),
    ]

    FUNCTIONALITY_CHOICES = [
        ('All tools working', 'All tools working'),
        ('Minor repairs needed', 'Minor repairs needed'),
        ('Major repairs needed', 'Major repairs needed'),
    ]

    BATH_CLEANLINESS_CHOICES = [
        ('Clean and hygienic', 'Clean and hygienic'),
        ('Needs minor cleaning', 'Needs minor cleaning'),
        ('Requires thorough cleaning', 'Requires thorough cleaning'),
    ]

    SUPPLIES_CHOICES = [
        ('Water supply', 'Water supply'),
        ('Paper towels', 'Paper towels'),
        ('Proper lighting', 'Proper lighting'),
        ('Waste bin (not full)', 'Waste bin (not full)'),
        ('Hand soap', 'Hand soap'),
        ('Toilet paper', 'Toilet paper'),
        ('Hand dryer', 'Hand dryer'),
    ]

    EXTINGUISHER_CHOICES = [
        ('All present and current', 'All present and current'),
        ('Some need attention', 'Some need attention'),
        ('Critical issues', 'Critical issues'),
    ]

    EMERGENCY_CHOICES = [
        ('Clear and marked', 'Clear and marked'),
        ('Partially obstructed', 'Partially obstructed'),
        ('Blocked or unmarked', 'Blocked or unmarked'),
    ]
    
    back_lot_cleanliness = models.CharField(max_length=40, choices=BACKLOT_CLEANLINESS_CHOICES, blank=True, null=True)
    back_lot_maintenance = models.CharField(max_length=40, choices=MAINTENANCE_CHOICES, blank=True, null=True)
    front_yard_cleanliness = models.CharField(max_length=40, choices=FRONT_CLEANLINESS_CHOICES, blank=True, null=True)
    front_yard_landscaping = models.CharField(max_length=40, choices=LANDSCAPING_CHOICES, blank=True, null=True)
    inventory_status = models.CharField(max_length=40, choices=INVENTORY_CHOICES, blank=True, null=True)
    missing_tools = models.CharField(max_length=255, blank=True, null=True)  
    tool_cleanliness = models.CharField(max_length=40, choices=TOOL_CLEANLINESS_CHOICES, blank=True, null=True)
    tool_functionality = models.CharField(max_length=40, choices=FUNCTIONALITY_CHOICES, blank=True, null=True)
    bathroom_cleanliness = models.CharField(max_length=40, choices=BATH_CLEANLINESS_CHOICES, blank=True, null=True)
    bathroom_maintenance = models.CharField(max_length=40, choices=MAINTENANCE_CHOICES, blank=True, null=True)
    supplies = models.CharField(max_length=40, choices=SUPPLIES_CHOICES, blank=True, null=True)
    extinguisher_status = models.CharField(max_length=40, choices=EXTINGUISHER_CHOICES, blank=True, null=True)
    emergency_exit_status = models.CharField(max_length=40, choices=EMERGENCY_CHOICES, blank=True, null=True)
    notes = models.TextField(null=True, blank=True) 
    date = models.CharField(max_length=100,null=True, blank=True)
    submitted_by = models.CharField(max_length=100,null=True, blank=True)
    saved_on = models.DateField(null=True, blank=True)



    def __str__(self):
        return f"Inspection for {self.station.name}"


class Vehicle_inspection(models.Model):
    INSPECTION_TYPE_CHOICES = [
        ('regular maintenance', 'Regular Maintenance'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
    ]
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True, blank=True)
    station = models.ForeignKey(Station, related_name="vehicle_inspections", on_delete=models.CASCADE)
    type = models.CharField(max_length=40, choices=INSPECTION_TYPE_CHOICES,null=True, blank=True)
    technician = models.ForeignKey(UserProfile, on_delete=models.CASCADE,null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    submitted_by = models.CharField(max_length=100,null=True, blank=True)
    saved_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.type.capitalize()} Service - {self.vehicle.number} on {self.date}"
    
    class Meta:
        verbose_name = "Vehicle_service"
        verbose_name_plural = "Vehicle_services"


class Fleet_order(models.Model):
    URGENCY_LEVEL_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('pending approval', 'Pending Approval'),
    ]
    ORDER_TYPE_CHOICES = [
        ('fleet', 'Fleet'),
        ('office supplies', 'Office Supplies'),
    ]
    station = models.ForeignKey(Station, related_name="station_orders", on_delete=models.CASCADE)
    type = models.CharField(max_length=40, choices=ORDER_TYPE_CHOICES,null=True, blank=True)
    urgency_level = models.CharField(max_length=40,choices=URGENCY_LEVEL_CHOICES,null=True, blank=True)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES,default='pending approval',null=True, blank=True)
    item_description = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    quantity = models.IntegerField(null=False, blank=False)
    requested_by = models.CharField(max_length=100,null=True, blank=True)
    submitted_by = models.CharField(max_length=100,null=True, blank=True)
    approved_on = models.DateField(null=True, blank=True)
    saved_on = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.urgency_level.capitalize()} Order - {self.status} on {self.date}"
