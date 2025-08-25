# models.py
from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings

image_storage = FileSystemStorage() if settings.DEBUG else MediaCloudinaryStorage()

# Department model
class Department(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    # Each department has one manager
    manager = models.OneToOneField(
        "UserProfile",  
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="managed_department"
    )


    def __str__(self):
        return self.title


class UserProfile(models.Model):
    EMPLOYEE_CHOICES = [
        ("llc/field", "LLC/Field"),
        ("llc/owner", "LLC/Owner"),
        ("sales", "Sales"),
        ("field", "Field"),
        ("driver", "Driver"),
        ("manager", "Manager"),
        ("rwh", "RWH"),
        ("technician", "Technician"),
        ("admin", "Admin"),
        ("warehouse", "Warehouse"),
        ("mover", "Mover"),
        ("customers- per trevor", "Customers- Per Trevor"),
        ("vp", "VP"),
        ("ceo", "CEO"),
    ]

    MANAGEMENT_ROLES = {"manager"}
    SENIOR_MANAGEMENT_ROLES = {"llc/owner", "vp", "ceo"}
    ADMIN_ROLES = {"admin"}
    EMPLOYEE_ROLES = {
        "llc/field", "sales", "field", "driver", "rwh",
        "technician", "warehouse", "mover", "customers- per trevor"
    }

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    role = models.CharField(max_length=50, choices=EMPLOYEE_CHOICES, default="driver")
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        storage=image_storage,
        blank=True,
        null=True
    )

    phone_regex = RegexValidator(
        regex=r'^(?:\+1\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$',
        message="Phone number must be entered in the format: '+1234567890'."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Format: +1234567890"
    )

    start_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    hobbies = models.TextField(blank=True, help_text="Optional: List hobbies comma-separated")
    favourite_quote = models.TextField(blank=True, help_text="Your favorite inspirational quote")

    is_admin = models.BooleanField(default=False)
    is_senior_management = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    def save(self, *args, **kwargs):
        """
        Automatically update the stored boolean fields before saving.
        """
        # Admin check
        self.is_admin = (self.role in self.ADMIN_ROLES) or self.user.is_staff or self.user.is_superuser

        # Senior management check
        self.is_senior_management = self.role in self.SENIOR_MANAGEMENT_ROLES

        # Manager check (either role is 'manager' or has team members)
        # Note: On initial save, self.pk may be None, so can't check team_members yet
        self.is_manager = (self.role in self.MANAGEMENT_ROLES)

        # Employee check
        self.is_employee = (
            not self.is_admin
            and not self.is_senior_management
            and self.role in self.EMPLOYEE_ROLES
        )

        super().save(*args, **kwargs)

    @property
    def tenure_days(self):
        if self.start_date:
            return (timezone.now().date() - self.start_date).days
        return None

    @property
    def tenure_string(self):
        if not self.start_date:
            return "N/A"
        delta = timezone.now().date() - self.start_date
        years = delta.days // 365
        months = (delta.days % 365) // 30
        return f"{years} year(s), {months} month(s)"


class Goal(models.Model):
    GOAL_TYPE_CHOICES = [
        ('short_term', 'Short-Term'),
        ('long_term', 'Long-Term'),
    ]
    
    title = models.CharField(max_length=200, help_text="Goal title")
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPE_CHOICES, default='short_term', help_text="Type of goal")
    description = models.TextField(help_text="Detailed description of the goal")
    assigned_to = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='assigned_goals',
        help_text="Employee assigned to this goal"
    )
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='created_goals',
        help_text="Manager or senior management who created this goal"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(
        blank=True,
        null = True,
        help_text="Action plans for improvement"
    )
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Goal"
        verbose_name_plural = "Goals"
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to}"
