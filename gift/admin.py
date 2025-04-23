from django.contrib import admin
from gift.models import Gift_company, Gift_card, Award
from django.utils.html import format_html



class Award_Admin(admin.ModelAdmin):
    def employee_names(self, obj):
        if obj.employees.exists():
            employees = obj.employees.all()
            employee_list = ", ".join([emp.user.username for emp in employees])
            return format_html('<span style="color: #4CAF50;">{}</span>', employee_list)
        else:
            return "No employees assigned" 
    
    employee_names.short_description = 'Employees'

    list_display = ['date_award', 'employee_names', 'card', 'amount', 'reason', 'awarded_by', 'date_saved']
    list_filter = ['employees', 'awarded_by']
    search_fields = ['employees__user__username', 'awarded_by__user__username']


class Gift_Card_Admin(admin.ModelAdmin):
    def sequential_id(self, obj):
        return obj.pk  

    sequential_id.short_description = 'ID' 

    list_display = ["sequential_id", "company", "amount", "date_of_purchase", "added_by"]
    search_fields = ["company__name", "added_by__username"]
    list_filter = ["added_by", "company"]
    ordering = ('-date_of_purchase',)


admin.site.register(Gift_company)
admin.site.register(Gift_card, Gift_Card_Admin)
admin.site.register(Award, Award_Admin)
