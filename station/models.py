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


class Truck_inspection(models.Model):

    CLEAN_STATUS_CHOICES = [
        ('full of trash & dirt', 'Full of Trash & Dirt'),
        ('free of trash', 'Free of Trash'),
        ('removed trash', 'Removed Trash'),
    ]
    TRASH_CLEAN_STATUS_CHOICES=[
        ('not clean','Not Clean'),
        ('dirty now clean','Dirty Now Clean'),
        ('already clean','Already Clean'),
    ]
    GENERAL_CHOICES = [
        ('missing-not restocked', 'Missing-Not Restocked'),
        ('missing restocked', 'Missing Restocked'),
        ('present', 'Present'),
    ]
    SPARE_TYRE_CHOICES=[
        ('good','Good'),
        ('normal','Normal'),
        ('damage','Damage'),
    ]

    # Truck and Date Information
    date = models.DateField(null=True, blank=True)
    truck = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True, blank=True,limit_choices_to={'vehicle_type': 'truck'})
    
    # Trash & Clean Status
    clean_status = models.CharField(max_length=50, choices=CLEAN_STATUS_CHOICES, null=True, blank=True)
    in_cab = models.CharField(max_length=50, choices=TRASH_CLEAN_STATUS_CHOICES, null=True, blank=True)
    bed_of_truck = models.CharField(max_length=50, choices=TRASH_CLEAN_STATUS_CHOICES, null=True, blank=True)
    
    # In Cab
    first_aid_kit = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    floor_mats = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    business_cards = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    business_cards_magnetic = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    fuses = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    two_pens = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    sharpie = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    camera = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    flash_light = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    sun_visor = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    geo_tab = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    jack_and_links = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    cab_card = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    registration = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    insurance_card = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    accident_report_form = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    process_of_accident = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)

    # Tool Box
    fire_extinguisher = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    expiry_date_fe = models.DateField(null=True, blank=True)
    four_way = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    min_7_orange = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    hazard_triangle_x3 = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    jumper_cables = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    large_door_stops = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    trash_bag = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    roll_paper_towels = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    small_hand = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    bottle_jack = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    
    # Equipment Checklist
    cones = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    spare_tire = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    condition_spare_tyre = models.CharField(max_length=50, choices=SPARE_TYRE_CHOICES, null=True, blank=True)

    # saving information
    saved_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True)
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Truck {self.truck} Inspection on {self.date}"


class Trailer_inspection(models.Model):

    CLEAN_STATUS_CHOICES = [
        ('full of trash & dirt', 'Full of Trash & Dirt'),
        ('free of trash', 'Free of Trash'),
        ('removed trash', 'Removed Trash'),
        ('detailed inside/out', 'Detailed Inside/Out'),
        ('wiped down inside/ washed outside', 'Wiped Down Inside/ Washed Outside'),
        ('wiped down inside only', 'Wiped Down Inside Only'),
        ('washed outside only', 'Washed Outside Only'),
    ]
    GENERAL_CHOICES = [
        ('missing-not restocked', 'Missing-Not Restocked'),
        ('missing restocked', 'Missing Restocked'),
        ('present', 'Present'),
    ]
    
    # Trailer and Date Information
    date = models.DateField(null=True, blank=True)
    trailer = models.ForeignKey(Vehicle, on_delete=models.CASCADE,null=True, blank=True,limit_choices_to={'vehicle_type': 'trailer'})
    
    # Trailer Trash Status
    clean_status = models.CharField(max_length=50, choices=CLEAN_STATUS_CHOICES, null=True, blank=True)
    trash = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    
    # Equipment Checklist
    blanket_84 = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    hand_trucks_with_covers = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    four_wheel_dolly = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    short_straps = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    long_straps = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    ramp = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    rubber_bands = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    red_floor_runner = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    forearm_straps = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    wardrobe_boxes_with_bars = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    tv_box_for_rental = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    multi_tool_set = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    hand_tools_bag = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    two_carabiner = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)
    broom = models.CharField(max_length=50, choices=GENERAL_CHOICES, null=True, blank=True)

    # Saving Information
    saved_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True) 
    date_saved = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Trailer {self.trailer} Inspection on {self.date}"


