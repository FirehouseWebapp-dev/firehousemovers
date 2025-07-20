from django.db import models
from django.contrib.auth.models import User
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.storage import FileSystemStorage
from django.core.validators import RegexValidator
from django.utils import timezone
from django.conf import settings

image_storage = FileSystemStorage() if settings.DEBUG else MediaCloudinaryStorage()

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
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    # Role with dropdown choices
    role = models.CharField(max_length=50, choices=EMPLOYEE_CHOICES, default="driver")

    # Cloudinary or local storage depending on DEBUG
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        storage=image_storage,
        blank=True,
        null=True
    )

    # Phone with validation
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

    def __str__(self):
        return self.user.get_full_name() or self.user.username

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
