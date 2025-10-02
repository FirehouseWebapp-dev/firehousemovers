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
    slug = models.SlugField(max_length=100, null=True, blank=True, help_text="URL-friendly identifier (not editable)")
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
    SENIOR_MANAGEMENT_ROLES = { "vp", "ceo"}
    ADMIN_ROLES = {"admin"}
    EMPLOYEE_ROLES = {
        "llc/field", "sales", "field", "driver", "rwh", "llc/owner",
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
        Automatically update boolean flags from role, but preserve manual admin
        overrides done through the admin site or other forms.
        """
        # Fetch original instance to detect which flags were explicitly changed
        original = None
        if self.pk:
            try:
                original = UserProfile.objects.get(pk=self.pk)
            except UserProfile.DoesNotExist:
                original = None

        computed_is_admin = (self.role in self.ADMIN_ROLES) or self.user.is_staff or self.user.is_superuser
        computed_is_senior_management = self.role in self.SENIOR_MANAGEMENT_ROLES
        computed_is_manager = (self.role in self.MANAGEMENT_ROLES)
        computed_is_employee = (
            not computed_is_admin
            and not computed_is_senior_management
            and self.role in self.EMPLOYEE_ROLES
        )

        # Only overwrite flags that were NOT explicitly changed by the caller
        if original is None or self.is_admin == original.is_admin:
            self.is_admin = computed_is_admin

        if original is None or self.is_senior_management == original.is_senior_management:
            self.is_senior_management = computed_is_senior_management

        if original is None or self.is_manager == original.is_manager:
            self.is_manager = computed_is_manager

        if original is None or self.is_employee == original.is_employee:
            self.is_employee = computed_is_employee

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


