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
    # --- Senior mgmt reviews ---
    path("reviews/", views.regular_reviews, name="regular_reviews"),
    path("reviews/cycle/<int:cycle_id>/", views.cycle_assignments, name="cycle_assignments"),
    path("reviews/evaluate/<int:evaluation_id>/", views.evaluate_manager, name="evaluate_manager"),
    path("reviews/my/", views.my_manager_reviews, name="my_manager_reviews"),
    path("reviews/detail/<int:evaluation_id>/", views.manager_review_detail, name="manager_review_detail"),
    path("reviews/pending/", views.senior_pending_reviews, name="senior_pending_reviews"),  
]

from . import views_dynamic

# Management UI
urlpatterns += [
    path("forms/", views_dynamic.evalform_list, name="evalform_list"),
    path("forms/new/", views_dynamic.evalform_create, name="evalform_create"),
    path("forms/<int:pk>/", views_dynamic.evalform_detail, name="evalform_detail"),
    path("forms/<int:pk>/edit/", views_dynamic.evalform_edit, name="evalform_edit"),
    path("forms/<int:pk>/preview/", views_dynamic.evalform_preview, name="evalform_preview"),
    path("forms/<int:pk>/activate/", views_dynamic.evalform_activate, name="evalform_activate"),
    path("forms/<int:form_id>/questions/add/", views_dynamic.question_add, name="question_add"),
    path("forms/questions/<int:question_id>/edit/", views_dynamic.question_edit, name="question_edit"),
    path("forms/questions/<int:question_id>/choices/add/", views_dynamic.choice_add, name="choice_add"),
]
