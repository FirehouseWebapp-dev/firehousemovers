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


class ReportFilterForm(forms.Form):
    REPORT_CHOICES = [
        ("overall", "Overall"),
        ("date_range", "By Date Range"),
    ]
    report_type = forms.ChoiceField(
        choices=REPORT_CHOICES,
        label="Report Type",
        widget=forms.Select(attrs={"id": "id_report_type", "class": "border rounded px-2 py-1"})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "border rounded px-2 py-1", "id": "id_start_date"}
        )
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "border rounded px-2 py-1", "id": "id_end_date"}
        )
    )

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("report_type") == "date_range":
            if not cleaned.get("start_date") or not cleaned.get("end_date"):
                raise forms.ValidationError("Both start and end dates are required for a date-range report.")
        return cleaned
