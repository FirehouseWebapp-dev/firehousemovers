from django.contrib import admin
from .models import UserProfile


class UserAdmin(admin.ModelAdmin):
    list_display = ["user", "role"]
    search_fields = ["role", "user"]
    list_filter = ["role"]


admin.site.register(UserProfile, UserAdmin)
