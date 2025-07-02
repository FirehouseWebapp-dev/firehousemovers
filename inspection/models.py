from django.db import models
from authentication.models import UserProfile
from vehicle.models import Crew, Vehicle
from decimal import Decimal
from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage


class Truck_inspection(models.Model):

    CLEAN_STATUS_CHOICES = [
        ("full of trash & dirt", "Full of Trash & Dirt"),
        ("free of trash", "Free of Trash"),
        ("removed trash", "Removed Trash"),
    ]
    TRASH_CLEAN_STATUS_CHOICES = [
        ("not clean", "Not Clean"),
        ("dirty now clean", "Dirty Now Clean"),
        ("already clean", "Already Clean"),
    ]
    GENERAL_CHOICES = [
        ("missing-not restocked", "Missing-Not Restocked"),
        ("missing restocked", "Missing Restocked"),
        ("present", "Present"),
    ]
    SPARE_TYRE_CHOICES = [
        ("good", "Good"),
        ("normal", "Normal"),
        ("damage", "Damage"),
    ]

    # Truck and Date Information
    date = models.DateField(null=True, blank=True)
    truck = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"vehicle_type": "truck"},
    )

    # Trash & Clean Status
    clean_status = models.CharField(
        max_length=50, choices=CLEAN_STATUS_CHOICES, null=True, blank=True
    )
    in_cab = models.CharField(
        max_length=50, choices=TRASH_CLEAN_STATUS_CHOICES, null=True, blank=True
    )
    bed_of_truck = models.CharField(
        max_length=50, choices=TRASH_CLEAN_STATUS_CHOICES, null=True, blank=True
    )

    # In Cab
    first_aid_kit = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    floor_mats = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    business_cards = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    business_cards_magnetic = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    fuses = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    two_pens = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    sharpie = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    camera = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    flash_light = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    sun_visor = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    geo_tab = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    jack_and_links = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    cab_card = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    registration = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    insurance_card = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    accident_report_form = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    process_of_accident = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )

    # Tool Box
    fire_extinguisher = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    expiry_date_fe = models.DateField(null=True, blank=True)
    four_way = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    min_7_orange = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    hazard_triangle_x3 = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    jumper_cables = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    large_door_stops = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    trash_bag = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    roll_paper_towels = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    small_hand = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    bottle_jack = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )

    # Equipment Checklist
    cones = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    spare_tire = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    condition_spare_tyre = models.CharField(
        max_length=50, choices=SPARE_TYRE_CHOICES, null=True, blank=True
    )

    # saving information
    saved_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, null=True, blank=True
    )
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Truck {self.truck} Inspection on {self.date}"


class Trailer_inspection(models.Model):

    CLEAN_STATUS_CHOICES = [
        ("full of trash & dirt", "Full of Trash & Dirt"),
        ("free of trash", "Free of Trash"),
        ("removed trash", "Removed Trash"),
        ("detailed inside/out", "Detailed Inside/Out"),
        ("wiped down inside/ washed outside", "Wiped Down Inside/ Washed Outside"),
        ("wiped down inside only", "Wiped Down Inside Only"),
        ("washed outside only", "Washed Outside Only"),
    ]
    GENERAL_CHOICES = [
        ("missing-not restocked", "Missing-Not Restocked"),
        ("missing restocked", "Missing Restocked"),
        ("present", "Present"),
    ]

    # Trailer and Date Information
    date = models.DateField(null=True, blank=True)
    trailer = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        limit_choices_to={"vehicle_type": "trailer"},
    )

    # Trailer Trash Status
    clean_status = models.CharField(
        max_length=50, choices=CLEAN_STATUS_CHOICES, null=True, blank=True
    )
    trash = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )

    # Equipment Checklist
    blanket_84 = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    hand_trucks_with_covers = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    four_wheel_dolly = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    short_straps = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    long_straps = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    ramp = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    rubber_bands = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    red_floor_runner = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    forearm_straps = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    wardrobe_boxes_with_bars = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    tv_box_for_rental = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    multi_tool_set = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    hand_tools_bag = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    two_carabiner = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )
    broom = models.CharField(
        max_length=50, choices=GENERAL_CHOICES, null=True, blank=True
    )

    # Saving Information
    saved_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, null=True, blank=True
    )
    date_saved = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Trailer {self.trailer} Inspection on {self.date}"


class Onsite_inspection(models.Model):

    # Basic Information
    saved_on = models.DateTimeField(auto_now_add=True)
    job_number = models.CharField(max_length=100, unique=True)
    inspector = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="inspector_inspections"
    )
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=20)
    pickup_address = models.TextField()
    delivery_address = models.TextField()
    crew_leader = models.ForeignKey(
        Crew,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="crew_leader_inspections",
    )
    crew_members = models.ManyToManyField(
        Crew, blank=True, related_name="crew_member_inspections"
    )

    # Prior to Move
    materials_check_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    vehicle_inventory_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    customer_communication_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    parking_arranged_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )

    # At Pickup
    customer_greeted_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    crew_introduction_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    initial_walkthrough_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    estimate_comparison_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    damage_inspection_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    paperwork_signed_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    valuables_secured_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    protection_setup_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    photos_sent_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    inventory_management_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    furniture_disassembly_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    parts_management_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    loading_quality_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    padding_used_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    load_secured_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    final_walkthrough_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    customer_initials_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    follow_instructions_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    truck_prepared_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    dispatch_complete_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )

    # At Drop Off
    dispatch_unload_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    damage_inspection_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    protection_setup_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    placement_accuracy_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    pad_management_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    furniture_reassembly_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    customer_walkthrough_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    vehicle_inspection_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    final_charges_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    customer_review_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    paperwork_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    payment_collection_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    video_testimonial_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )
    completion_notice_rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)], null=True, blank=True
    )

    # Final Review
    comments = models.TextField(blank=True, null=True)
    customer_feedback = models.TextField(blank=True, null=True)
    prior_move_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0, null=True, blank=True
    )
    pickup_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0, null=True, blank=True
    )
    dropoff_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0, null=True, blank=True
    )
    overall_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        # Calculate the scores before saving
        self.prior_move_score = self.calculate_prior_move_score()
        self.pickup_score = self.calculate_pickup_score()
        self.dropoff_score = self.calculate_dropoff_score()
        self.overall_score = self.calculate_overall_score()

        # Call the super method to save the object
        super().save(*args, **kwargs)

    def calculate_prior_move_score(self):
        """
        Calculate the prior move score based on ratings for actions prior to the move.
        Ensures that ratings are converted to integers if they are not already.
        """
        ratings = [
            self.materials_check_rating,
            self.vehicle_inventory_rating,
            self.customer_communication_rating,
            self.parking_arranged_rating,
        ]

        # Convert all ratings to integers if they are not None and not already integers
        converted_ratings = []
        for rating in ratings:
            if rating is not None:
                if isinstance(rating, str):
                    try:
                        converted_ratings.append(int(rating))
                    except ValueError:
                        continue
                else:
                    converted_ratings.append(int(rating))

        # Filter out None values and calculate the average
        if converted_ratings:
            score = sum(converted_ratings) / len(converted_ratings)
            return round(Decimal(score), 2)

        return Decimal(0.0)

    def calculate_pickup_score(self):
        """
        Calculate the pickup score based on ratings for the pickup process.
        Ensures that ratings are converted to integers if they are not already.
        """
        ratings = [
            self.customer_greeted_rating,
            self.crew_introduction_rating,
            self.initial_walkthrough_rating,
            self.estimate_comparison_rating,
            self.damage_inspection_rating,
            self.paperwork_signed_rating,
            self.valuables_secured_rating,
            self.protection_setup_rating,
            self.photos_sent_rating,
            self.inventory_management_rating,
            self.furniture_disassembly_rating,
            self.parts_management_rating,
            self.loading_quality_rating,
            self.padding_used_rating,
            self.load_secured_rating,
            self.final_walkthrough_rating,
            self.customer_initials_rating,
            self.follow_instructions_rating,
            self.truck_prepared_rating,
            self.dispatch_complete_rating,
        ]

        # Convert all ratings to integers if they are not None and not already integers
        converted_ratings = []
        for rating in ratings:
            if rating is not None:
                if isinstance(rating, str):
                    try:
                        converted_ratings.append(int(rating))
                    except ValueError:
                        continue  # If conversion fails, skip that rating
                else:
                    converted_ratings.append(int(rating))

        # Filter out None values and calculate the average
        if converted_ratings:
            score = sum(converted_ratings) / len(converted_ratings)
            return round(Decimal(score), 2)

        return Decimal(0.0)  # Return 0.0 if no ratings are available

    def calculate_dropoff_score(self):
        """
        Calculate the dropoff score based on ratings for the dropoff process.
        Ensures that ratings are converted to integers if they are not already.
        """
        ratings = [
            self.dispatch_unload_rating,  # Dropoff version
            self.damage_inspection_rating,
            self.protection_setup_rating,
            self.placement_accuracy_rating,
            self.pad_management_rating,
            self.furniture_reassembly_rating,
            self.customer_walkthrough_rating,
            self.vehicle_inspection_rating,
            self.final_charges_rating,
            self.customer_review_rating,
            self.paperwork_rating,
            self.payment_collection_rating,
            self.video_testimonial_rating,
            self.completion_notice_rating,
        ]

        # Convert all ratings to integers if they are not None and not already integers
        converted_ratings = []
        for rating in ratings:
            if rating is not None:
                if isinstance(rating, str):
                    try:
                        converted_ratings.append(int(rating))
                    except ValueError:
                        continue  # If conversion fails, skip that rating
                else:
                    converted_ratings.append(int(rating))

        # Filter out None values and calculate the average
        if converted_ratings:
            score = sum(converted_ratings) / len(converted_ratings)
            return round(Decimal(score), 2)

        return Decimal(0.0)  # Return 0.0 if no ratings are available

    def calculate_overall_score(self):
        """
        Calculate the overall score as the average of prior_move_score, pickup_score, and dropoff_score.
        Ensures that scores are handled as Decimal values and converted to integers.
        """
        prior_move_score = self.calculate_prior_move_score()
        pickup_score = self.calculate_pickup_score()
        dropoff_score = self.calculate_dropoff_score()

        # Calculate the overall score as the average of the three individual scores
        total_score = (prior_move_score + pickup_score + dropoff_score) / Decimal(3)
        return round(total_score, 2)

    def get_final_review(self):
        """
        Returns a summary of the final review with all scores.
        """
        scores = {
            "Prior to Move Score": self.prior_move_score,
            "Pickup Score": self.pickup_score,
            "Dropoff Score": self.dropoff_score,
            "Overall Score": self.overall_score,
        }

        return (
            f"Prior to Move Score: {scores['Prior to Move Score']}/5\n"
            f"Pickup Score: {scores['Pickup Score']}/5\n"
            f"Dropoff Score: {scores['Dropoff Score']}/5\n"
            f"Overall Score: {scores['Overall Score']}/5"
        )

    def __str__(self):
        return f"inspector : {self.inspector} - Job # {self.job_number}"

def inspection_upload_to(instance, filename):
    """
    Puts files under either:
      - dev_inspections/…  (when DEBUG=True)
      - prod_inspections/… (when DEBUG=False)
    """
    folder = "dev_inspections" if settings.DEBUG else "prod_inspections"
    return f"{folder}/inspection_photos/{filename}"

class OnsiteInspectionImage(models.Model):
    inspection  = models.ForeignKey(
        Onsite_inspection,
        related_name="images",
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        upload_to=inspection_upload_to,
        storage=default_storage
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.inspection.job_number} – {self.image.name}"
