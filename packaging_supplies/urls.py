from django.urls import path
from packaging_supplies.views import (
    index,
    pull_material,
    return_material,
    OrderMaterialView,
    record_receipt,
    update_order_status
)

app_name = 'packaging_supplies'

urlpatterns = [
    path("", index, name="index"),
    path("pull/", pull_material, name="pull_material"),
    path("return/", return_material, name="return_material"),
    path("order/", OrderMaterialView.as_view(), name="order_material"),
    path("receipts/", record_receipt, name="record_receipt"),
    path("order/<int:order_id>/<str:status>/", update_order_status, name="update_order_status"),
]
