from django.urls import path
from .views import (
    excel_view,
    order_view,
    report_view,
    save_excel_changes,
    station_view,
    station_inspection_view,
    vehicle_inspection_view,
)

urlpatterns = [
    path("", station_view, name="station"),
    path("report/<int:station_number>/", report_view.as_view(), name="report"),
    path(
        "station-inspection/<int:station_number>/",
        station_inspection_view.as_view(),
        name="station_inspection",
    ),
    path(
        "vehicle-inspection/<int:station_number>/<str:vehicle>/",
        vehicle_inspection_view.as_view(),
        name="vehicle_inspection",
    ),
    path("order/<int:station_number>/<str:type>/", order_view.as_view(), name="order"),
    path("excel/<int:station_number>/", excel_view, name="excel_station_1"),
    path("save-excel/<int:station_number>/", save_excel_changes, name="save_excel_changes"),
]
