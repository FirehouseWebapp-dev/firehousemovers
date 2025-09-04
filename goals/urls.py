from django.urls import path
from . import views

app_name = "goals"

urlpatterns = [
    path('goals_management/', views.goals_management, name='goal_management'),
    path('view/<int:employee_id>/', views.view_goals, name='view_goals'),
    path('add/<int:employee_id>/', views.add_goals, name='add_goals'),
    path('edit/<int:goal_id>/', views.edit_goal, name='edit_goal'),
    path('remove/<int:goal_id>/', views.remove_goal, name='remove_goal'),
    path('toggle-completion/<int:goal_id>/', views.toggle_goal_completion, name='toggle_goal_completion'),
    path('my_goals/', views.my_goals, name='my_goals'),
    path("send-schedule-email/", views.send_schedule_email, name="send_schedule_email"),
]
