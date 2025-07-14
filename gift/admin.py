from django.contrib import admin
from gift.models import Gift_company, Gift_card, Award, AwardCategory
from django.utils.html import format_html
from django import forms

class Gift_Card_Admin(admin.ModelAdmin):
    def sequential_id(self, obj):
        return obj.pk  

    sequential_id.short_description = 'ID' 

    list_display = ["sequential_id", "company", "amount", "date_of_purchase", "added_by"]
    search_fields = ["company__name", "added_by__user__username"]
    list_filter = ["added_by", "company"]
    ordering = ('-date_of_purchase',)


class AwardAdminForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        card = cleaned_data.get("card")
        amount = cleaned_data.get("amount")

        if category and category.name.lower() == "gift_card":
            if not card:
                self.add_error("card", "Card is required for Gift Card awards.")
            if not amount:
                self.add_error("amount", "Amount is required for Gift Card awards.")
        return cleaned_data


class Award_Admin(admin.ModelAdmin):
    form = AwardAdminForm

    def employee_name(self, obj):
        if obj.employees:
            return format_html('<span style="color: #4CAF50;">{}</span>', obj.employees.user.username)
        else:
            return "No employee assigned"

    employee_name.short_description = 'Employee'

    list_display = ['date_award', 'employee_name', 'card', 'amount', 'reason', 'awarded_by', 'date_saved']
    list_filter = ['employees', 'awarded_by']
    search_fields = ['employees__user__username', 'awarded_by__user__username']


admin.site.register(Gift_company)
admin.site.register(Gift_card, Gift_Card_Admin)
admin.site.register(Award, Award_Admin)
admin.site.register(AwardCategory)
