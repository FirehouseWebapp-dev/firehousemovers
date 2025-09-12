from django.urls import path
from . import views
from . import views_dynamic

app_name = "evaluation"

urlpatterns = [
    path("dashboard/", views.evaluation_dashboard, name="dashboard"),
    path("dashboard2/", views_dynamic.evaluation_dashboard2, name="dashboard2"),
    path("evaluate/<int:evaluation_id>/", views.evaluate_employee, name="evaluate"),
    path("evaluate-dynamic/<int:evaluation_id>/", views_dynamic.evaluate_dynamic_employee, name="evaluate_dynamic"),
    path("dynamic-evaluation/<int:evaluation_id>/", views_dynamic.view_dynamic_evaluation, name="view_dynamic_evaluation"),
    path("pending/", views.pending_evaluation_view, name="pending"),
    path("pending-v2/", views_dynamic.pending_evaluations_v2, name="pending_v2"),
    path("my-evaluations/", views.my_evaluations, name="my_evaluations"),
    path("my-evaluations-v2/", views_dynamic.my_evaluations_v2, name="my_evaluations_v2"),
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

# Management UI
urlpatterns += [
    path("forms/", views_dynamic.evalform_list, name="evalform_list"),
    path("forms/new/", views_dynamic.evalform_create, name="evalform_create"),
    path("forms/<int:pk>/", views_dynamic.evalform_detail, name="evalform_detail"),
    path("forms/<int:pk>/edit/", views_dynamic.evalform_edit, name="evalform_edit"),
    path("forms/<int:pk>/preview/", views_dynamic.evalform_preview, name="evalform_preview"),
    path("forms/<int:pk>/activate/", views_dynamic.evalform_activate, name="evalform_activate"),
    path("forms/<int:pk>/delete/", views_dynamic.evalform_delete, name="evalform_delete"),
    path("forms/<int:form_id>/questions/add/", views_dynamic.question_add, name="question_add"),
    path("forms/questions/<int:question_id>/edit/", views_dynamic.question_edit, name="question_edit"),
    path("forms/questions/<int:question_id>/delete/", views_dynamic.question_delete, name="question_delete"),
    path("forms/questions/<int:question_id>/choices/add/", views_dynamic.choice_add, name="choice_add"),
    path("forms/<int:pk>/update_order/", views_dynamic.update_question_order, name="update_question_order"),
]
