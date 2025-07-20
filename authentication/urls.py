from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
  LoginView, 
  LogoutView, 
  SignUpView, 
  check_email_availability,
  profile_view, view_profile,
  CustomPasswordChangeView,
  team_view, add_team_member, remove_team_member
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
    path("profile/<int:user_id>/", view_profile, name="view_profile"),  # ← This line
    path(
        "password/change/",
        CustomPasswordChangeView.as_view(),  # <-- Use this instead of auth_views
        name="password_change"
    ),
    path('team/', team_view, name='team'),
    path('team/add/', add_team_member, name='add_team_member'),
    path("team/remove/<int:user_id>/", remove_team_member, name="remove_team_member"),
]
