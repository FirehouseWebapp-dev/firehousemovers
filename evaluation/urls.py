from django.urls import path
from . import views

app_name = "evaluation"

urlpatterns = [
    path("dashboard/", views.evaluation_dashboard, name="dashboard"),
    path("evaluate/<int:evaluation_id>/", views.evaluate_employee, name="evaluate"),
    path("pending/", views.pending_evaluation_view, name="pending"),
    path("my-evaluations/", views.my_evaluations, name="my_evaluations"),
    path("my-evaluations/<int:evaluation_id>/", views.evaluation_detail, name="my_evaluation_detail"),
    path("analytics/", views.analytics_dashboard, name="analytics"),
    path("api/team-totals/",            views.team_totals_api,            name="team_totals_api"),
    path("api/metrics/",                views.metrics_api,                name="metrics_api"),
    path("api/metrics-by-employee/",    views.metrics_by_employee_api,    name="metrics_by_employee_api"),
]
