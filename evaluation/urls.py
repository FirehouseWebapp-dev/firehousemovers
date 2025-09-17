from django.urls import path
from . import views

app_name = "evaluation"

urlpatterns = [
    # Main evaluation routes
    path("dashboard/", views.evaluation_dashboard, name="dashboard"),
    path("evaluate/<int:evaluation_id>/", views.evaluate_employee, name="evaluate"),
    path("dynamic-evaluation/<int:evaluation_id>/", views.view_evaluation, name="view_evaluation"),
    path("pending/", views.pending_evaluations, name="pending"),
    path("my-evaluations/", views.my_evaluations_v2, name="my_evaluations"),
    
    # Manager evaluations (dynamic)
    path("manager-evaluations/", views.manager_evaluation_dashboard, name="manager_evaluation_dashboard"),
    path("manager-evaluations/cards/", views.manager_evaluation_dashboard, name="manager_evaluation_cards"),
    path("manager-evaluations/cards/detail/", views.manager_evaluation_cards_detail, name="manager_evaluation_cards_detail"),
    path("manager-evaluations/evaluate/<int:evaluation_id>/", views.evaluate_manager, name="evaluate_manager_dynamic"),
    path("manager-evaluations/view/<int:evaluation_id>/", views.view_manager_evaluation, name="view_manager_evaluation"),
    path("manager-evaluations/my/", views.my_manager_evaluations, name="my_manager_evaluations"),
    path("manager-evaluations/pending/", views.pending_manager_evaluations, name="pending_manager_evaluations"),  
]

# Analytics Dashboard (Senior Management)
urlpatterns += [
    path("analytics/", views.senior_manager_analytics_dashboard, name="senior_analytics_dashboard"),
    path("analytics/department/<int:department_id>/", views.analytics_department_detail, name="analytics_department_detail"),
    path("analytics/team/<int:team_leader_id>/", views.analytics_team_detail, name="analytics_team_detail"),
    path("analytics/export/", views.analytics_export, name="analytics_export"),
    path("analytics/trends/", views.analytics_trends, name="analytics_trends"),
    path("analytics/alerts/", views.analytics_alerts, name="analytics_alerts"),
]

# Management UI
urlpatterns += [
    path("forms/", views.evalform_list, name="evalform_list"),
    path("forms/new/", views.evalform_create, name="evalform_create"),
    path("forms/<int:pk>/", views.evalform_detail, name="evalform_detail"),
    path("forms/<int:pk>/edit/", views.evalform_edit, name="evalform_edit"),
    path("forms/<int:pk>/preview/", views.evalform_preview, name="evalform_preview"),
    path("forms/<int:pk>/activate/", views.evalform_activate, name="evalform_activate"),
    path("forms/<int:pk>/delete/", views.evalform_delete, name="evalform_delete"),
    path("forms/<int:form_id>/questions/add/", views.question_add, name="question_add"),
    path("forms/questions/<int:question_id>/edit/", views.question_edit, name="question_edit"),
    path("forms/questions/<int:question_id>/delete/", views.question_delete, name="question_delete"),
    path("forms/questions/<int:question_id>/choices/add/", views.choice_add, name="choice_add"),
    path("forms/<int:pk>/update_order/", views.update_question_order, name="update_question_order"),
]
