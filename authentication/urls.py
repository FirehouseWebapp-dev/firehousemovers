from django.urls import path
from .views import LoginView, LogoutView, check_email_availability

app_name = "authentication"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "ajax/check_email_availability/",
        check_email_availability,
        name="check_email_availability",
    ),
]
