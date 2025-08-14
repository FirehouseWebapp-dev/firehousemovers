from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
from authentication.models import UserProfile
from .models import Award, AwardCategory, HallOfFameEntry
from .forms import AwardForm, AwardCategoryForm, GiftCardForm, AwardCardForm, HallOfFameForm
from authentication.mailer import send_gift_card_email
import re


# Helper function for permission
def is_manager_or_admin(user):
    if not hasattr(user, "userprofile"):
        return False
    return user.userprofile.role in ["manager", "admin"]

# ------------------------
# Dashboard
# ------------------------
class DashboardView(ListView):
    model = Award
    template_name = "awards/dashboard.html"
    context_object_name = "awards"

    def get_queryset(self):
        qs = super().get_queryset().select_related("category", "employees")

        # Filters
        category_id = self.request.GET.get("category")
        month = self.request.GET.get("month")
        year = self.request.GET.get("year")

        if category_id:
            qs = qs.filter(category__id=category_id)

        if month:
            qs = qs.filter(date_award__month=month)

        if year:
            qs = qs.filter(date_award__year=year)

        return qs.order_by("-date_award")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = AwardCategory.objects.all()
        context["selected_category"] = self.request.GET.get("category", "")
        context["selected_month"] = self.request.GET.get("month", "")
        context["selected_year"] = self.request.GET.get("year", "")
        context["years"] = Award.objects.dates('date_award', 'year', order='DESC')
        context["months"] = [
            {"value": "01", "name": "January"},
            {"value": "02", "name": "February"},
            {"value": "03", "name": "March"},
            {"value": "04", "name": "April"},
            {"value": "05", "name": "May"},
            {"value": "06", "name": "June"},
            {"value": "07", "name": "July"},
            {"value": "08", "name": "August"},
            {"value": "09", "name": "September"},
            {"value": "10", "name": "October"},
            {"value": "11", "name": "November"},
            {"value": "12", "name": "December"},
        ]
        return context


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


# why kwargs or simple line, which one is better?

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
       
        kwargs["current_user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.awarded_by = UserProfile.objects.get(user=self.request.user)
        return super().form_valid(form)

class AwardUpdateView(LoginRequiredMixin, ManagerOrAdminMixin, UpdateView):
    model = Award
    form_class = AwardForm
    template_name = "awards/edit_award.html"
    success_url = reverse_lazy("awards:dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["current_user"] = self.request.user
        return kwargs

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
        form = AwardCardForm(request.POST, current_user=request.user)
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
        form = AwardCardForm(current_user=request.user)
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


class PrizesDescriptionView(TemplateView):
    template_name = "awards/prizes_description.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = AwardCategory.objects.all().order_by("name")
        return context

class HallOfFameView(ListView):
    model = HallOfFameEntry
    template_name = "awards/hall_of_fame.html"
    context_object_name = "entries"

class HallOfFameListView(View):
    template_name = "awards/hall_of_fame.html"

    def get(self, request):
        entries = HallOfFameEntry.objects.all().order_by("-created_at")

        # Year filter
        years = HallOfFameEntry.objects.dates("created_at", "year", order="DESC")
        selected_year = request.GET.get("year")
        if selected_year:
            entries = entries.filter(created_at__year=selected_year)

        return render(request, self.template_name, {
            "entries": entries,
            "years": [y.year for y in years],
            "selected_year": selected_year,
        })

class HallOfFameCreateView(View):
    template_name = "awards/hall_of_fame_add.html"

    def get(self, request):
        form = HallOfFameForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = HallOfFameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("awards:hall_of_fame")
        return render(request, self.template_name, {"form": form})


class HallOfFameView(View):
    template_name = "awards/hall_of_fame.html"

    def get(self, request):
        form = HallOfFameForm()
        entries = HallOfFameEntry.objects.all().order_by("-created_at")

        # Get years for filter
        years = HallOfFameEntry.objects.dates("created_at", "year", order="DESC")
        selected_year = request.GET.get("year")
        if selected_year:
            entries = entries.filter(created_at__year=selected_year)

        return render(request, self.template_name, {
            "form": form,
            "entries": entries,
            "years": [y.year for y in years],
            "selected_year": selected_year,
        })

    def post(self, request):
        form = HallOfFameForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("awards:hall_of_fame")
        entries = HallOfFameEntry.objects.all().order_by("-created_at")
        years = HallOfFameEntry.objects.dates("created_at", "year", order="DESC")
        return render(request, self.template_name, {
            "form": form,
            "entries": entries,
            "years": [y.year for y in years],
            "selected_year": None,
        })

class HallOfFameUpdateView(LoginRequiredMixin, ManagerOrAdminMixin, UpdateView):
    model = HallOfFameEntry
    form_class = HallOfFameForm
    template_name = "awards/hall_of_fame_add.html"  # You can create a separate edit template if you'd like
    success_url = reverse_lazy("awards:hall_of_fame")

class HallOfFameDeleteView(LoginRequiredMixin, ManagerOrAdminMixin, DeleteView):
    model = HallOfFameEntry
    template_name = "awards/confirm_delete_award.html"  # Reuse or create a new confirm template
    success_url = reverse_lazy("awards:hall_of_fame")

from django.utils.timezone import now

@login_required
def my_awards_view(request):
    profile = UserProfile.objects.get(user=request.user)
    awards = Award.objects.filter(employees=profile).order_by("-date_award")
    hall_of_fame_entries = HallOfFameEntry.objects.filter(employee=request.user.id).order_by("-created_at")


    return render(request, "awards/my_awards.html", {
        "awards": awards,
        "hall_of_fame_entries": hall_of_fame_entries,
    })