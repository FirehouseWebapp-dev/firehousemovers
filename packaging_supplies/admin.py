from django.contrib import admin
from .models import Material, OrderReceipt

class MaterialAdmin(admin.ModelAdmin):
    list_display = ('transaction_type', 'job_id', 'trailer_number', 'employee', 'date', 'status')

admin.site.register(Material, MaterialAdmin)
admin.site.register(OrderReceipt)
