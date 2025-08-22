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
  department_view,
  add_department,
  edit_department,
  remove_department,
   
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
    path("department/", department_view, name="department"),
    path("department/add/", add_department, name="add_department"),
    path("department/edit/<int:pk>/", edit_department, name="edit_department"),
    path("department/remove/<int:pk>/", remove_department, name="remove_department"),
    
]
