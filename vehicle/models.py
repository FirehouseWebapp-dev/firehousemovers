from django.db import models
from authentication.models import UserProfile


class Crew(models.Model):
    name = models.CharField(max_length=100, unique=True)
    role = models.CharField(
        max_length=50,
        choices=[("leader", "Leader"), ("member", "Member")],
        default="member",
    )

    def __str__(self):
        return self.name


# Vehicle Information Model
class Vehicle(models.Model):
    TYPE_CHOICES = [
        ("truck", "Truck"),
        ("trailer", "Trailer"),
    ]
    name = models.CharField(max_length=100, null=True, blank=True)
    vehicle_type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, null=True, blank=True
    )
    number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    last_inspection_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle_type.capitalize()} - ({self.number})"


# Availability Data Model
class AvailabilityData(models.Model):
    vehicle = models.ForeignKey(
        Vehicle,
        related_name="availabilities",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=50,
        choices=[("In Service", "In Service"), ("Out of Service", "Out of Service")],
        null=True,
        blank=True,
    )
    estimated_back_in_service_date = models.DateField(null=True, blank=True)
    back_in_service_date = models.DateField(null=True, blank=True)
    date_saved = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = [
            "vehicle",
            "start_date",
        ]  # Ensures only one availability per vehicle per day

    def __str__(self):
        return f"{self.vehicle.vehicle_type.capitalize()} {self.vehicle.number} - {self.status}"


# Job Orders Model
class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    date = models.DateField(null=True, blank=True)
    job_no = models.CharField(max_length=50, unique=True, null=True, blank=True)
    last_name_customer = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    type_of_move = models.CharField(max_length=100, null=True, blank=True)
    moved_before = models.BooleanField(default=False, null=True, blank=True)
    moved_before_crew_name = models.CharField(max_length=100, null=True, blank=True)
    referral_source = models.CharField(max_length=100, null=True, blank=True)
    crew_name = models.ForeignKey(
        Crew, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    crew_available = models.BooleanField(default=False, null=True, blank=True)
    number_of_trucks = models.PositiveIntegerField(null=True, blank=True)
    number_of_trailers = models.PositiveIntegerField(null=True, blank=True)
    notes_order_detail = models.TextField(null=True, blank=True)
    saved_by = models.CharField(max_length=100, null=True, blank=True)
    saved_on = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Job {self.job_no} - {self.last_name_customer}"


# Job Dispatch Model
class Dispatch(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Completed",
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="dispatches"
    )
    ipad = models.CharField(max_length=50, null=True, blank=True)
    crew_leads = models.ForeignKey(
        Crew, on_delete=models.DO_NOTHING, null=True, blank=True
    )
    drivers = models.CharField(max_length=100, null=True, blank=True)
    truck_1 = models.CharField(max_length=50, null=True, blank=True)
    trailer_1 = models.CharField(max_length=50, null=True, blank=True)
    truck_2 = models.CharField(max_length=50, null=True, blank=True)
    trailer_2 = models.CharField(max_length=50, null=True, blank=True)
    truck_3 = models.CharField(max_length=50, null=True, blank=True)
    trailer_3 = models.CharField(max_length=50, null=True, blank=True)
    truck_4 = models.CharField(max_length=50, null=True, blank=True)
    trailer_4 = models.CharField(max_length=50, null=True, blank=True)
    material = models.CharField(max_length=200, null=True, blank=True)
    special_equipment_needed = models.CharField(max_length=200, null=True, blank=True)
    special_equipment_status = models.CharField(max_length=200, null=True, blank=True)
    speedy_inventory_account = models.CharField(max_length=100, null=True, blank=True)
    speedy_inventory = models.CharField(max_length=200, null=True, blank=True)
    labels_for_speedy_inventory = models.CharField(
        max_length=200, null=True, blank=True
    )
    notes_dispatcher = models.TextField(null=True, blank=True)
    submitted_by = models.CharField(max_length=100, null=True, blank=True)
    submitted_on = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Job: {self.order.job_no} - {self.order.last_name_customer}"


class Evaluation(models.Model):
    job = models.ForeignKey(Dispatch, on_delete=models.CASCADE, null=True, blank=True)
    inspector = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, null=True, blank=True
    )
    customer_feedback = models.TextField(null=True, blank=True)
    overall_rating = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    total_duration = models.DurationField(null=True, blank=True)

    def calculate_total_duration(self):
        if self.start_time and self.end_time:
            self.total_duration = self.end_time - self.start_time
            self.save()

    def __str__(self):
        return f"Evaluation for Job {self.job.job_no} by {self.inspector.username}"
