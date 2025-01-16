from django.urls import path
from .views import  inspection_view, order_view, report_view, station_view,station_inspection_view,truck_inspection_view, vehicle_inspection_view,trailer_inspection_view,inspection_report_view

urlpatterns = [
    path('', station_view, name='station'),
    path('inspection/', inspection_view, name='inspection'),
    path('report/<int:station_number>/', report_view.as_view(), name='report'),
    path('inspection-report/', inspection_report_view.as_view(), name='inspection_report'),
    path('station-inspection/<int:station_number>/', station_inspection_view.as_view(), name='station_inspection'),
    path('vehicle-inspection/<int:station_number>/<str:vehicle>/', vehicle_inspection_view.as_view(), name='vehicle_inspection'),
    path('order/<int:station_number>/<str:type>/', order_view.as_view(), name='order'),
    path('trailer-inspection/', trailer_inspection_view.as_view(), name='trailer_inspection'),
    path('truck-inspection/', truck_inspection_view.as_view(), name='truck_inspection'),
]
