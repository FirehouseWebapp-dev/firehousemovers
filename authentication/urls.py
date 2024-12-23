from django.urls import path
from .views import SignUpView,check_email_availability,LoginView,LogoutView

app_name = "authentication"

urlpatterns = [
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "ajax/check_email_availability/",
        check_email_availability,
        name="check_email_availability",
    ),
]
