from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.contrib.auth import get_user_model

from .models import MarketingPhoto, Vendor, PromotionalItem, PromotionalItemTransaction
from .forms import VendorForm, PromotionalItemForm, PromotionalItemRemoveForm

# Import permissions
from rest_framework.permissions import IsAuthenticated
from inventory_app.permissions import IsManager

User = get_user_model()

class PhotoUploadView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        photos = MarketingPhoto.objects.order_by("-uploaded_at")
        can_delete = request.user.is_staff
        if hasattr(request.user, "userprofile") and request.user.userprofile.role == "manager":
            can_delete = True
        return render(request, "marketing/photos.html", {
            "photos": photos,
            "can_delete": can_delete,
        })

    def post(self, request):
        files = request.FILES.getlist("photos")
        if not files:
            messages.error(request, "Please select or capture at least one image.")
            return redirect("marketing:photos")
        for img in files:
            MarketingPhoto.objects.create(image=img)
        messages.success(request, "Photos uploaded successfully!")
        return redirect("marketing:photos")


class PhotoDeleteView(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, pk):
        photo = get_object_or_404(MarketingPhoto, pk=pk)
        photo.delete()
        messages.success(request, "Photo deleted.")
        return redirect("marketing:photos")


class VendorListCreateView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = VendorForm()
        vendors = Vendor.objects.order_by("name")
        return render(request, "marketing/vendors.html", {"form": form, "vendors": vendors})

    def post(self, request):
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor added!")
            return redirect("marketing:vendors")
        vendors = Vendor.objects.order_by("name")
        return render(request, "marketing/vendors.html", {"form": form, "vendors": vendors})


class PromotionalItemView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    template_name = "marketing/items.html"

    def get(self, request):
        return render(request, self.template_name, {
            "add_form": PromotionalItemForm(),
            "remove_form": PromotionalItemRemoveForm(),
            "items": PromotionalItem.objects.all(),
            "transactions": PromotionalItemTransaction.objects.order_by("-timestamp"),
        })

    def post(self, request):
        if "add_item" in request.POST:
            add_form = PromotionalItemForm(request.POST)
            remove_form = PromotionalItemRemoveForm()
            if add_form.is_valid():
                add_form.save()
                messages.success(request, "Item added!")
                return redirect("marketing:items")
        else:
            remove_form = PromotionalItemRemoveForm(request.POST)
            add_form = PromotionalItemForm()
            if remove_form.is_valid():
                item = remove_form.cleaned_data["item"]
                qty = remove_form.cleaned_data["quantity"]
                reason = remove_form.cleaned_data["reason"]
                item.quantity = max(item.quantity - qty, 0)
                item.save()
                PromotionalItemTransaction.objects.create(item=item, action="remove", quantity=qty, reason=reason)
                messages.success(request, "Item removed!")
                return redirect("marketing:items")

        return render(request, self.template_name, {
            "add_form": add_form,
            "remove_form": remove_form,
            "items": PromotionalItem.objects.all(),
            "transactions": PromotionalItemTransaction.objects.order_by("-timestamp"),
        })


class ReportsView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        report_type = request.GET.get("report_type")
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date")

        start_date = parse_date(start_date_str) if start_date_str else None
        end_date = parse_date(end_date_str) if end_date_str else None

        data = []
        show_report = False

        if report_type == "vendor":
            qs = Vendor.objects.all()
            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)
            show_report = True
            data = qs.order_by("name")
        elif report_type == "item":
            qs = PromotionalItem.objects.all()
            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)
            show_report = True
            data = qs.order_by("name")

        return render(request, "marketing/reports.html", {
            "report_type": report_type,
            "start_date": start_date_str,
            "end_date": end_date_str,
            "data": data,
            "show_report": show_report,
        })
