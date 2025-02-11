from django.shortcuts import render,redirect
from django.views import View
from rest_framework.permissions import IsAuthenticated
from django.http import HttpResponseForbidden
from authentication.models import UserProfile
from gift.forms import AwardCardForm, GiftCardForm
from datetime import datetime
from django.contrib import messages
from inventory_app.permissions import IsManager


class GiftCardView(View):
    permission_classes = [IsAuthenticated, IsManager] 

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self,request):
        form = GiftCardForm()
        return render(request, "gift_card.html",{"form":form})


    def post(self,request):
        form = GiftCardForm(request.POST)
        if form.is_valid():
            gift_card=form.save(commit=False)
            current_user=request.user
            user=UserProfile.objects.get(user=current_user)
            gift_card.added_by=user
            gift_card.save()

            messages.success(request,"Gift Card Added Successfully!")
            return redirect('gift_card')
        else:
            messages.error(request,form.errors)
            form = GiftCardForm()
        
        return render(request, "gift_card.html",{"form":form})


class AwardCardView(View):
    permission_classes = [IsAuthenticated, IsManager] 

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self,request):
        form = AwardCardForm()
        return render(request, "award_card.html",{"form":form})


    def post(self,request):
        form = AwardCardForm(request.POST)
        if form.is_valid():
            emp=form.cleaned_data['employee_name']
            gift_card=form.save(commit=False)
            current_user=request.user
            user=UserProfile.objects.get(user=current_user)
            gift_card.awarded_by=user
            gift_card.date_saved=datetime.now()
            gift_card.save()

            messages.success(request,f"Gift Card Awarded to {emp}!")
            return redirect('award_card')
        else:
            messages.error(request, form.errors)
            form = AwardCardForm()
        
        return render(request, "award_card.html",{"form":form})
