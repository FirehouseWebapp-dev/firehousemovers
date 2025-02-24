from django.urls import path
from .views import (
    JobLogisticsPage,
    availability_logistic_view,
    logistic_report,
    vehicle_availability_view,
    availability_report,
)

urlpatterns = [
    path(
        "availability-logitics/",
        availability_logistic_view,
        name="availability_logitics",
    ),
    path(
        "vehicle-availability/",
        vehicle_availability_view.as_view(),
        name="vehicle_availability",
    ),
    path("job-logistics/", JobLogisticsPage.as_view(), name="job_logistics"),
    path("logistic-report/", logistic_report.as_view(), name="logistic_report"),
    path(
        "availability-report/",
        availability_report.as_view(),
        name="availability_report",
    ),
]
