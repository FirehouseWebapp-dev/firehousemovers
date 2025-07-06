from django import forms
from django.forms.widgets import ClearableFileInput
from .models import Vendor, PromotionalItem

# ─── Custom multiple‐file widget ──────────────────────────────────────────
class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True
# ─────────────────────────────────────────────────────────────────────────


class MarketingPhotoForm(forms.Form):
    photos = forms.FileField(
        widget=MultiFileInput(attrs={"multiple": True}),
        label="Capture Marketing Photos",
        help_text="Select one or more image files"
    )

    def clean_photos(self):
        files = self.files.getlist("photos")
        if not files:
            raise forms.ValidationError("You must select at least one image.")
        # optional: ensure every file is an image
        for f in files:
            if not f.content_type.startswith("image/"):
                raise forms.ValidationError("Only image files are allowed.")
        return files

class VendorForm(forms.ModelForm):
    class Meta:
        model  = Vendor
        fields = ["name", "contact_info"]

class PromotionalItemForm(forms.ModelForm):
    class Meta:
        model  = PromotionalItem
        fields = ["name", "quantity"]

class PromotionalItemRemoveForm(forms.Form):
    item     = forms.ModelChoiceField(queryset=PromotionalItem.objects.all())
    quantity = forms.IntegerField(min_value=1)
    reason   = forms.CharField(max_length=300, required=False)
