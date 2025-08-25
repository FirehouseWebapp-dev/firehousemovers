from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from .views import (
  LoginView, 
  LogoutView, 
  SignUpView, 
  check_email_availability,
  profile_view, view_profile,
  CustomPasswordChangeView,
  team_view, add_team_member, 
  remove_team_member, edit_team_member,
  goals_management_view,
  add_goals_view,
  view_goals_view,
  edit_goal_view,
  remove_goal_view,
  toggle_goal_completion_view,
   
)

app_name = "authentication"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),  # <-- ✅ Add this
    path(
        "ajax/check_email_availability/",
        check_email_availability,
        name="check_email_availability",
    ),
    path("profile/", profile_view, name="profile"),
    path('profile/<int:user_id>/', view_profile, name='view_profile'),
    path(
        "password/change/",
        CustomPasswordChangeView.as_view(),  # <-- Use this instead of auth_views
        name="password_change"
    ),
    path('team/', team_view, name='team'),
    path('team/add/', add_team_member, name='add_team_member'),
    path("team/remove/<int:user_id>/", remove_team_member, name="remove_team_member"),
    path("profile/edit/<int:user_id>/", edit_team_member, name="edit_profile"),
    path(
        "password-reset/", 
        auth_views.PasswordResetView.as_view(
            template_name="authentication/password_reset_form.html", 
            email_template_name="authentication/password_reset_email.txt",  # plain text fallback
            html_email_template_name="authentication/password_reset_email.html",
            subject_template_name="authentication/password_reset_subject.txt",  # optional
            success_url=reverse_lazy("authentication:password_reset_done")  # ✅ important!
        ), 
        name="password_reset"
    ),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(
        template_name="authentication/password_reset_done.html"
    ), name="password_reset_done"),

    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="authentication/password_reset_confirm.html",
        success_url=reverse_lazy("authentication:password_reset_complete")
    ), name="password_reset_confirm"),

    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(
        template_name="authentication/password_reset_complete.html"
    ), name="password_reset_complete"),

    # Goals Management URLs
    path("goals/", goals_management_view, name="goals_management"),
    path("goals/add/<int:employee_id>/", add_goals_view, name="add_goals"),
    path("goals/view/<int:employee_id>/", view_goals_view, name="view_goals"),
    path("goals/edit/<int:goal_id>/", edit_goal_view, name="edit_goal"),
    path("goals/remove/<int:goal_id>/", remove_goal_view, name="remove_goal"),
    path("goals/toggle-completion/<int:goal_id>/", toggle_goal_completion_view, name="toggle_goal_completion"),
    
]
