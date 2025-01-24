from django.urls import path
from .views import  truck_inspection_view,trailer_inspection_view,inspection_report_view,onsite_inspection_view,inspection_view

urlpatterns = [
    path('inspection/', inspection_view, name='inspection'),
    path('onsite-inspection/', onsite_inspection_view.as_view(), name='onsite_inspection'),
    path('inspection-report/', inspection_report_view.as_view(), name='inspection_report'),
    path('trailer-inspection/', trailer_inspection_view.as_view(), name='trailer_inspection'),
    path('truck-inspection/', truck_inspection_view.as_view(), name='truck_inspection'),
]
