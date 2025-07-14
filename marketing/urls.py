from django.urls import path
from .views import (
    PhotoUploadView,
    PhotoDeleteView,
    VendorListCreateView,
    PromotionalItemView,
    ReportsView,
)

app_name = "marketing"

urlpatterns = [
    path("photos/", PhotoUploadView.as_view(), name="photos"),
    path("photos/<int:pk>/delete/", PhotoDeleteView.as_view(), name="photo-delete"),
    path("vendors/", VendorListCreateView.as_view(), name="vendors"),
    path("items/", PromotionalItemView.as_view(), name="items"),
    path("reports/", ReportsView.as_view(), name="reports"),
]
