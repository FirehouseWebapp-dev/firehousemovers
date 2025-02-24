from django.contrib import admin
from gift.models import Gift_company, Gift_card, Award


class Award_Admin(admin.ModelAdmin):
    list_display = ["employee_name", "card", "date_award", "amount"]
    search_fields = ["awarded_by", "card", "employee_name", "amount"]
    list_filter = ["awarded_by", "card"]


class Gift_Card_Admin(admin.ModelAdmin):
    list_display = ["company", "amount", "date_of_purchase", "added_by"]
    search_fields = ["company", "added_by"]
    list_filter = ["added_by", "company"]


admin.site.register(Gift_company)
admin.site.register(Gift_card, Gift_Card_Admin)
admin.site.register(Award, Award_Admin)
