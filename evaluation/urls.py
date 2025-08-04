from django.urls import path
from . import views

app_name = "evaluation"

urlpatterns = [
    path("dashboard/", views.evaluation_dashboard, name="dashboard"),
    path("evaluate/<int:evaluation_id>/", views.evaluate_employee, name="evaluate"),
    path("pending/", views.pending_evaluation_view, name="pending"),
]
