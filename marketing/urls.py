# marketing/urls.py
from django.urls import path
from .views import (
    PhotoUploadView,
    PhotoDeleteView,
    VendorListCreateView,
    PromotionalItemView,
)

app_name = "marketing"

urlpatterns = [
    # /marketing/photos/       → list & upload
    path("photos/", PhotoUploadView.as_view(), name="photos"),
    # /marketing/photos/123/delete/ → staff-only delete
    path("photos/<int:pk>/delete/", PhotoDeleteView.as_view(), name="photo-delete"),

    # /marketing/vendors/      → list & add vendors
    path("vendors/", VendorListCreateView.as_view(), name="vendors"),

    # /marketing/items/        → add/remove promotional items
    path("items/", PromotionalItemView.as_view(), name="items"),
]
