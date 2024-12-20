from django.urls import path
from .views import home, inventory_list, add_inventory, add_employee, issue_uniform,SignUpView,check_email_availability

app_name = "inventory_app"

urlpatterns = [
    path('', home, name='home'),
    path("signup/", SignUpView.as_view(), name="signup"),
    path('inventory/', inventory_list, name='inventory_list'),
    path('inventory/add/', add_inventory, name='add_inventory'),
    path('employee/add/', add_employee, name='add_employee'),
    path('uniform/issue/', issue_uniform, name='issue_uniform'),
    path(
        "ajax/check_email_availability/",
        check_email_availability,
        name="check_email_availability",
    ),
]
