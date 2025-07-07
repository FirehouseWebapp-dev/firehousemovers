import os
from django.conf import settings
from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.storage import FileSystemStorage

def marketing_photo_upload_to(inst, fn):
    base = "dev_marketing" if settings.DEBUG else "prod_marketing"
    return os.path.join(base, "photos", fn)

# Pick storage explicitly
_storage = FileSystemStorage() if settings.DEBUG else MediaCloudinaryStorage()

class MarketingPhoto(models.Model):
    image = models.ImageField(upload_to=marketing_photo_upload_to, storage=_storage)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id} @ {self.uploaded_at:%Y-%m-%d %H:%M}"

class Vendor(models.Model):
    name         = models.CharField(max_length=200, unique=True)
    contact_info = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class PromotionalItem(models.Model):
    name     = models.CharField(max_length=200, unique=True)
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

class PromotionalItemTransaction(models.Model):
    ACTION_CHOICES = [("add","Add"),("remove","Remove")]
    item      = models.ForeignKey(PromotionalItem, on_delete=models.CASCADE, related_name="transactions")
    action    = models.CharField(max_length=6, choices=ACTION_CHOICES)
    quantity  = models.PositiveIntegerField()
    reason    = models.CharField(max_length=300, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_action_display()} {self.quantity} of {self.item.name}"
