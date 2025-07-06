# marketing/views.py
from django.shortcuts      import render, redirect, get_object_or_404
from django.views          import View
from django.contrib        import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models   import MarketingPhoto, Vendor, PromotionalItem, PromotionalItemTransaction
from .forms    import VendorForm, PromotionalItemForm, PromotionalItemRemoveForm


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
    """
    GET:  show vendor list + empty form  
    POST: create a new Vendor or re-render with errors
    """
    def get(self, request):
        form    = VendorForm()
        vendors = Vendor.objects.order_by("name")
        return render(request, "marketing/vendors.html", {
            "form": form,
            "vendors": vendors,
        })

    def post(self, request):
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Vendor added!")
            return redirect("marketing:vendors")

        vendors = Vendor.objects.order_by("name")
        return render(request, "marketing/vendors.html", {
            "form": form,
            "vendors": vendors,
        })


class PromotionalItemView(LoginRequiredMixin, View):
    """
    Handles both adding and removing promotional items in one URL.
    """
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
                # adjust inventory + record transaction
                item.quantity = max(item.quantity - qty, 0)
                item.save()
                PromotionalItemTransaction.objects.create(
                    item=item, action="remove", quantity=qty, reason=reason
                )
                messages.success(request, "Item removed!")
                return redirect("marketing:items")

        # if we get here, one of the forms had errors
        return render(request, self.template_name, {
            "add_form":    add_form,
            "remove_form": remove_form,
            "items":       PromotionalItem.objects.all(),
            "transactions": PromotionalItemTransaction.objects.order_by("-timestamp"),
        })
