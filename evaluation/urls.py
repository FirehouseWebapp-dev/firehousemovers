from django.urls import path
from . import views_dynamic

app_name = "evaluation"

urlpatterns = [
    # Main evaluation routes
    path("dashboard/", views_dynamic.evaluation_dashboard2, name="dashboard"),
    path("evaluate/<int:evaluation_id>/", views_dynamic.evaluate_dynamic_employee, name="evaluate"),
    path("dynamic-evaluation/<int:evaluation_id>/", views_dynamic.view_dynamic_evaluation, name="view_dynamic_evaluation"),
    path("pending/", views_dynamic.pending_evaluations_v2, name="pending"),
    path("my-evaluations/", views_dynamic.my_evaluations_v2, name="my_evaluations"),
    
    # Manager evaluations (dynamic)
    path("manager-evaluations/", views_dynamic.manager_evaluation_dashboard, name="manager_evaluation_dashboard"),
    path("manager-evaluations/cards/", views_dynamic.manager_evaluation_dashboard, name="manager_evaluation_cards"),
    path("manager-evaluations/cards/detail/", views_dynamic.manager_evaluation_cards_detail, name="manager_evaluation_cards_detail"),
    path("manager-evaluations/evaluate/<int:evaluation_id>/", views_dynamic.evaluate_manager, name="evaluate_manager_dynamic"),
    path("manager-evaluations/view/<int:evaluation_id>/", views_dynamic.view_manager_evaluation, name="view_manager_evaluation"),
    path("manager-evaluations/my/", views_dynamic.my_manager_evaluations, name="my_manager_evaluations"),
    path("manager-evaluations/pending/", views_dynamic.pending_manager_evaluations, name="pending_manager_evaluations"),  
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
