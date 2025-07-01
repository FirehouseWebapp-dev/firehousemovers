# inspection/admin.py

from django.contrib import admin
from django.utils.html import format_html, format_html_join

from .models import (
    Truck_inspection,
    Trailer_inspection,
    Onsite_inspection,
    OnsiteInspectionImage,
)


class Onsite_inspection_Admin(admin.ModelAdmin):
    list_display = [
        "job_number",
        "inspector",
        "crew_leader",
        "customer_name",
        "saved_on",
    ]
    search_fields = [
        "job_number",
        "inspector__user__username",
        "crew_leader__user__username",
        "customer_name",
    ]
    list_filter = ["inspector", "crew_leader"]
    readonly_fields = ("preview_images",)

    def preview_images(self, obj):
        """
        Show thumbnails of all uploaded photos for this inspection.
        """
        qs = obj.images.all()
        if not qs:
            return "No images"
        return format_html_join(
            "",
            '<img src="{}" style="max-height:100px; margin:2px;" />',
            ((img.image.url,) for img in qs),
        )

    preview_images.short_description = "Photos Preview"


@admin.register(OnsiteInspectionImage)
class OnsiteInspectionImageAdmin(admin.ModelAdmin):
    list_display = ("inspection", "image_tag", "uploaded_at")
    readonly_fields = ("image_tag", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("inspection__job_number",)

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:100px; margin:2px;" />',
                obj.image.url,
            )
        return "-"
    image_tag.short_description = "Image Thumbnail"


# Register the other inspection models as before
admin.site.register(Truck_inspection)
admin.site.register(Trailer_inspection)
admin.site.register(Onsite_inspection, Onsite_inspection_Admin)
