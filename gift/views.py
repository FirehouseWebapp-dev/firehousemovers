from django.shortcuts import render, redirect
from django.views import View
from rest_framework.permissions import IsAuthenticated
from authentication.mailer import send_gift_card_email
from authentication.models import UserProfile
from gift.forms import AwardCardForm, GiftCardForm
from datetime import datetime
from django.contrib import messages
from inventory_app.permissions import IsManager
from django.utils import timezone
from django.http import JsonResponse
import re

class GiftCardView(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = GiftCardForm()
        return render(request, "gift_card.html", {"form": form})

    def post(self, request):
        form = GiftCardForm(request.POST)
        if form.is_valid():
            gift_card = form.save(commit=False)

            current_user = request.user
            user = UserProfile.objects.get(user=current_user)
            gift_card.added_by = user
            gift_card.date_of_purchase=timezone.now().date()
            gift_card.save()

            messages.success(request, "Gift Card Added Successfully!")
            return redirect("gift_card")
        else:
            messages.error(request, form.errors)
            form = GiftCardForm()

        return render(request, "gift_card.html", {"form": form})


class AwardCardView(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AwardCardForm()
        return render(request, "award_card.html", {"form": form})

    def post(self, request):
        form = AwardCardForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            employees = form.cleaned_data["employees"]
            card = form.cleaned_data["card"]
            reason = form.cleaned_data["reason"]
            email_text = request.POST.get('emails')

            # Parse emails from the text area (name <email@example.com>)
            email_pattern = r'[\w\.-]+@[\w\.-]+'  # This regex will match any valid email address
            emails = re.findall(email_pattern, email_text)
            
            # Save the Award instance without committing the ManyToManyField yet
            gift_card = form.save(commit=False)
            
            # Get the current user (the user who is awarding the gift card)
            current_user = request.user
            user = UserProfile.objects.get(user=current_user)
            gift_card.awarded_by = user
            gift_card.date_award = timezone.now().date()
            gift_card.date_saved = datetime.now()
            gift_card.save()  # Save the Award instance without saving the ManyToManyField yet

            # Save the ManyToManyField (employees) after the Award object is saved
            gift_card.employees.set(employees)  # Associate the employees with the Award instance
            gift_card.save()  # Save again to ensure the employees are saved properly

            # Prepare the employee usernames to display in the success message
            empl_usernames = [emp.user.username for emp in employees]
            empl_list = ", ".join(empl_usernames)

            # Show success message
            messages.success(request, f"Gift Card Awarded to {empl_list}!")
            try:
                send_gift_card_email(emails, card, reason)
            except Exception as e:
                print(f"Failed to send the email. Error: {str(e)}")
                messages.error(request, f"Failed to send the email. Error: {str(e)}")
            
            # Redirect to the award_card page after saving
            return redirect("award_card")
        
        else:
            # If the form is invalid, show error messages
            messages.error(request, form.errors)
            form = AwardCardForm()

        # Render the form again if not successful
        return render(request, "award_card.html", {"form": form})
    


def get_emails(request):
    employee_ids = request.GET.get('employee_ids')
    
    if employee_ids:
        employee_ids = employee_ids.split(',')
        employees = UserProfile.objects.filter(id__in=employee_ids)
        
        # Prepare the response with emails
        emails = [{"name": emp.user.username, "email": emp.user.email} for emp in employees]
        
        return JsonResponse({"emails": emails})
    return JsonResponse({"emails": []})