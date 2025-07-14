from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
import re

from authentication.models import UserProfile
from .models import Award, AwardCategory
from .forms import AwardForm, AwardCategoryForm, GiftCardForm, AwardCardForm
from authentication.mailer import send_gift_card_email
from inventory_app.permissions import IsManager

# Helper function for permission
def is_manager_or_admin(user):
    if not hasattr(user, "userprofile"):
        return False
    return user.userprofile.role in ["manager", "admin"]

# ------------------------
# Dashboard
# ------------------------
class DashboardView(LoginRequiredMixin, ListView):
    model = Award
    template_name = "awards/dashboard.html"
    context_object_name = "awards"
    ordering = ["-date_award"]

# ------------------------
# Award CRUD (CBVs)
# ------------------------
class ManagerOrAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return is_manager_or_admin(self.request.user)

class AwardCreateView(LoginRequiredMixin, ManagerOrAdminMixin, CreateView):
    model = Award
    form_class = AwardForm
    template_name = "awards/add_award.html"
    success_url = reverse_lazy("awards:dashboard")

    def form_valid(self, form):
        form.instance.awarded_by = UserProfile.objects.get(user=self.request.user)
        return super().form_valid(form)

class AwardUpdateView(LoginRequiredMixin, ManagerOrAdminMixin, UpdateView):
    model = Award
    form_class = AwardForm
    template_name = "awards/edit_award.html"
    success_url = reverse_lazy("awards:dashboard")

class AwardDeleteView(LoginRequiredMixin, ManagerOrAdminMixin, DeleteView):
    model = Award
    template_name = "awards/confirm_delete_award.html"
    success_url = reverse_lazy("awards:dashboard")

# ------------------------
# Award Category CRUD (CBVs)
# ------------------------
class CategoryListView(LoginRequiredMixin, ManagerOrAdminMixin, View):
    def get(self, request):
        categories = AwardCategory.objects.all().order_by("name")
        form = AwardCategoryForm()
        return render(request, "awards/category_list.html", {"categories": categories, "form": form})

    def post(self, request):
        form = AwardCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("awards:category_list")
        categories = AwardCategory.objects.all().order_by("name")
        return render(request, "awards/category_list.html", {"categories": categories, "form": form})

class CategoryUpdateView(LoginRequiredMixin, ManagerOrAdminMixin, UpdateView):
    model = AwardCategory
    form_class = AwardCategoryForm
    template_name = "awards/category_edit_form.html"
    success_url = reverse_lazy("awards:category_list")

class CategoryDeleteView(LoginRequiredMixin, ManagerOrAdminMixin, DeleteView):
    model = AwardCategory
    template_name = "awards/delete_category_confirm.html"
    success_url = reverse_lazy("awards:category_list")

# ------------------------
# Gift Card View (FBV)
# ------------------------
from django.contrib.auth.decorators import login_required

@login_required
def gift_card_view(request):
    if request.method == "POST":
        form = GiftCardForm(request.POST)
        if form.is_valid():
            gift_card = form.save(commit=False)
            user = UserProfile.objects.get(user=request.user)
            gift_card.added_by = user
            gift_card.date_of_purchase = timezone.now().date()
            gift_card.save()
            messages.success(request, "Gift Card Added Successfully!")
            return redirect("awards:gift_card")
        else:
            messages.error(request, form.errors)
    else:
        form = GiftCardForm()
    return render(request, "gift_card.html", {"form": form})

# ------------------------
# Award Card View (FBV)
# ------------------------
@login_required
def award_card_view(request):
    if request.method == "POST":
        form = AwardCardForm(request.POST)
        if form.is_valid():
            employees = form.cleaned_data["employees"]
            card = form.cleaned_data["card"]
            reason = form.cleaned_data["reason"]
            email_text = request.POST.get("emails")
            email_pattern = r"[\w\.-]+@[\w\.-]+"
            emails = re.findall(email_pattern, email_text)

            gift_card = form.save(commit=False)
            user = UserProfile.objects.get(user=request.user)
            gift_card.awarded_by = user
            gift_card.date_award = timezone.now().date()
            gift_card.date_saved = datetime.now()
            gift_card.save()
            gift_card.employees.set(employees)
            gift_card.save()

            empl_list = ", ".join([emp.user.username for emp in employees])
            messages.success(request, f"Gift Card Awarded to {empl_list}!")

            try:
                send_gift_card_email(emails, card, reason)
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
                messages.error(request, f"Failed to send email: {str(e)}")

            return redirect("awards:award_card")
        else:
            messages.error(request, form.errors)
    else:
        form = AwardCardForm()
    return render(request, "award_card.html", {"form": form})

# ------------------------
# Get Emails API (FBV)
# ------------------------
@login_required
def get_emails(request):
    employee_ids = request.GET.get("employee_ids")
    if employee_ids:
        employee_ids = employee_ids.split(",")
        employees = UserProfile.objects.filter(id__in=employee_ids)
        emails = [{"name": emp.user.username, "email": emp.user.email} for emp in employees]
        return JsonResponse({"emails": emails})
    return JsonResponse({"emails": []})
