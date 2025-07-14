from django.db import models
from django.core.exceptions import ValidationError
from authentication.models import UserProfile
import os
from django.conf import settings
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.storage import FileSystemStorage
from django.utils import timezone

class Gift_company(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Gift_card(models.Model):
    company = models.ForeignKey(Gift_company, on_delete=models.CASCADE)
    date_of_purchase = models.DateField(null=True, blank=True)
    amount = models.IntegerField(null=True, blank=True)
    added_by = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="added_by_user"
    )

    def clean(self):
        if self.amount:
            if self.amount < 1:
                raise ValidationError(
                    f"The Gift Card amount cannot be less then one ({self.amount})."
                )

    def __str__(self):
        return f"{self.id} - ({self.company }- {self.amount})"


class AwardCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    def clean(self):
        if len(self.name) < 3:
            raise ValidationError("Category name must be at least 3 characters.")
    
    def save(self, *args, **kwargs):
        self.name = self.name.strip().title()  # Capitalize each word
        super().save(*args, **kwargs)




def award_photo_upload_to(instance, filename):
    base = "dev_awards" if settings.DEBUG else "prod_awards"
    return os.path.join(base, "photos", filename)

award_storage = FileSystemStorage() if settings.DEBUG else MediaCloudinaryStorage()

class Award(models.Model):
    category = models.ForeignKey("AwardCategory", on_delete=models.CASCADE, default=1)
    date_award = models.DateField(default=timezone.now)
    employees = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="awards")
    card = models.ForeignKey("Gift_card", on_delete=models.CASCADE, related_name="gift_card", null=True, blank=True)
    amount = models.IntegerField(default=0)
    employee_photo = models.ImageField(upload_to=award_photo_upload_to, storage=award_storage, null=True, blank=True)
    reason = models.TextField(null=True, blank=True)
    awarded_by = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="awarded_user")
    date_saved = models.DateField(auto_now_add=True)

    def clean(self):
        if self.category and self.category.name == "gift_card":
            if not self.amount or not self.card:
                raise ValidationError("Gift Card awards require both card and amount.")
            if self.amount and self.card and self.amount > self.card.amount:
                raise ValidationError(
                    f"Award amount cannot exceed the gift card amount ({self.card.amount})."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Award, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.card}"
