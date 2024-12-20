from django.contrib import admin
from inventory_app.models import UserProfile, UniformAssignment, Inventory, Employee

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(UniformAssignment)
admin.site.register(Inventory)
admin.site.register(Employee)