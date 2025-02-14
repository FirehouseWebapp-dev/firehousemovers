from django.urls import path
from inventory_app.views import (
    Add_uniform_view,
    uniform_inventory_view,
    Issue_uniform_view,
    Return_uniform_view,
    Employee_view,
    Reports_view,
    inventory_view,
    get_uniforms,
    homeview,
)


urlpatterns = [
    path("", homeview, name="home"),
    path("inventory/", uniform_inventory_view, name="inventory"),
    path("uniform-add/", Add_uniform_view.as_view(), name="uniform_add"),
    path("uniform-issue/", Issue_uniform_view.as_view(), name="uniform_issue"),
    path("uniform-return/", Return_uniform_view.as_view(), name="uniform_return"),
    path("employee/", Employee_view.as_view(), name="employee"),
    path("reports/", Reports_view.as_view(), name="reports"),
    path("inventory-add/", inventory_view.as_view(), name="inventory_add"),
    path("inventory-remove/", inventory_view.as_view(), name="inventory_remove"),
    path("get-uniforms/", get_uniforms, name="get_uniforms"),
]
