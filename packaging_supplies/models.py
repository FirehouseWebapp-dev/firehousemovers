from django.db import models
from authentication.models import UserProfile
from vehicle.models import Vehicle

class Material(models.Model):
    TRANSACTION_TYPES = [
        ('pull', 'Pulling Materials'),
        ('return', 'Returning Materials'),
        ('order', 'Ordering Materials'),
    ]
    
    ORDER_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ]
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    job_id = models.CharField(max_length=50)
    trailer_number = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    employee = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='pending')
    
    # Material quantities
    small_boxes = models.IntegerField(default=0, null=True, blank=True)
    medium_boxes = models.IntegerField(default=0, null=True, blank=True)
    large_boxes = models.IntegerField(default=0, null=True, blank=True)
    xl_boxes = models.IntegerField(default=0, null=True, blank=True)
    wardrobe_boxes = models.IntegerField(default=0, null=True, blank=True)
    dish_boxes = models.IntegerField(default=0, null=True, blank=True)
    singleface_protection = models.IntegerField(default=0, null=True, blank=True)
    carpet_mask = models.IntegerField(default=0, null=True, blank=True)
    paper_pads = models.IntegerField(default=0, null=True, blank=True)
    packing_paper = models.IntegerField(default=0, null=True, blank=True)
    tape = models.IntegerField(default=0, null=True, blank=True)
    wine_boxes = models.IntegerField(default=0, null=True, blank=True)
    stretch_wrap = models.IntegerField(default=0, null=True, blank=True)
    tie_down_webbing = models.IntegerField(default=0, null=True, blank=True)
    packing_peanuts = models.IntegerField(default=0, null=True, blank=True)
    ram_board = models.IntegerField(default=0, null=True, blank=True)
    mattress_bags = models.IntegerField(default=0, null=True, blank=True)
    mirror_cartons = models.IntegerField(default=0, null=True, blank=True)
    bubble_wrap = models.IntegerField(default=0, null=True, blank=True)
    gondola_boxes = models.IntegerField(default=0, null=True, blank=True)
    
    employee_signature = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.job_id}"

class OrderReceipt(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='receipts')
    date_received = models.DateField()
    uploaded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Receipt for {self.material.job_id} - {self.date_received}"
    
    @property
    def transaction_type(self):
        return self.material.transaction_type
    
    @property
    def job_id(self):
        return self.material.job_id
    
    @property
    def trailer_number(self):
        return self.material.trailer_number
    
    @property
    def employee(self):
        return self.material.employee
    
    @property
    def material_quantities(self):
        return {
            'small_boxes': self.material.small_boxes,
            'medium_boxes': self.material.medium_boxes,
            'large_boxes': self.material.large_boxes,
            'xl_boxes': self.material.xl_boxes,
            'wardrobe_boxes': self.material.wardrobe_boxes,
            'dish_boxes': self.material.dish_boxes,
            'singleface_protection': self.material.singleface_protection,
            'carpet_mask': self.material.carpet_mask,
            'paper_pads': self.material.paper_pads,
            'packing_paper': self.material.packing_paper,
            'tape': self.material.tape,
            'wine_boxes': self.material.wine_boxes,
            'stretch_wrap': self.material.stretch_wrap,
            'tie_down_webbing': self.material.tie_down_webbing,
            'packing_peanuts': self.material.packing_peanuts,
            'ram_board': self.material.ram_board,
            'mattress_bags': self.material.mattress_bags,
            'mirror_cartons': self.material.mirror_cartons,
            'bubble_wrap': self.material.bubble_wrap,
            'gondola_boxes': self.material.gondola_boxes
        }
