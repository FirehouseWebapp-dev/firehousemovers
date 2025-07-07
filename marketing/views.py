from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from .models import MarketingPhoto, Vendor, PromotionalItem, PromotionalItemTransaction
from .forms import VendorForm, PromotionalItemForm, PromotionalItemRemoveForm
from django.utils.dateparse import parse_date

class PhotoUploadView(LoginRequiredMixin, View):
    """
    GET: show the camera/upload UI + gallery of existing photos
    POST: save any submitted 'photos' files and redirect back
    """
    def get(self, request):
        photos = MarketingPhoto.objects.order_by("-uploaded_at")
        return render(request, "marketing/photos.html", {
            "photos": photos,
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


class PhotoDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    View
):
    """
    Only staff can POST here to delete an existing MarketingPhoto.
    """
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, pk):
        photo = get_object_or_404(MarketingPhoto, pk=pk)
        photo.delete()
        messages.success(request, "Photo deleted.")
        return redirect("marketing:photos")


class VendorListCreateView(LoginRequiredMixin, View):
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

class PromotionalItemView(LoginRequiredMixin, View):
    template_name = "marketing/items.html"

    def get(self, request):
        return render(request, self.template_name, {
            "add_form":    PromotionalItemForm(),
            "remove_form": PromotionalItemRemoveForm(),
            "items":       PromotionalItem.objects.all(),
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
            add_form    = PromotionalItemForm()
            if remove_form.is_valid():
                item   = remove_form.cleaned_data["item"]
                qty    = remove_form.cleaned_data["quantity"]
                reason = remove_form.cleaned_data["reason"]
                item.quantity = max(item.quantity - qty, 0)
                item.save()
                PromotionalItemTransaction.objects.create(item=item, action="remove", quantity=qty, reason=reason)
                messages.success(request, "Item removed!")
                return redirect("marketing:items")
        return render(request, self.template_name, {
            "add_form":    add_form,
            "remove_form": remove_form,
            "items":       PromotionalItem.objects.all(),
            "transactions": PromotionalItemTransaction.objects.order_by("-timestamp"),
        })


class ReportsView(TemplateView):
    template_name = "marketing/reports.html"

    def get_context_data(self, **ctx):
        ctx = super().get_context_data(**ctx)
        report_type = self.request.GET.get("report_type")
        start_date_str = self.request.GET.get("start_date")
        end_date_str = self.request.GET.get("end_date")

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
            show_report = True  # always show report when user clicks Generate
            data = qs.order_by("name")
        elif report_type == "item":
            qs = PromotionalItem.objects.all()
            if start_date:
                qs = qs.filter(created_at__date__gte=start_date)
            if end_date:
                qs = qs.filter(created_at__date__lte=end_date)
            show_report = True
            data = qs.order_by("name")

        ctx["report_type"] = report_type
        ctx["start_date"] = start_date_str
        ctx["end_date"] = end_date_str
        ctx["data"] = data
        ctx["show_report"] = show_report

        return ctx
