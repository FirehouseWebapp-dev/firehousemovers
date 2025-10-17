from django.contrib import admin
from .models import LogType, CommunicationLog, LogResponse


@admin.register(LogType)
class LogTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(CommunicationLog)
class CommunicationLogAdmin(admin.ModelAdmin):
    list_display = ['subject', 'created_by', 'employee', 'log_type', 'event_date', 'is_acknowledged', 'acknowledgment_deadline', 'created_at']
    list_filter = ['log_type', 'visibility', 'is_acknowledged', 'requires_acknowledgment', 'created_at', 'event_date']
    search_fields = ['subject', 'content', 'employee__user__first_name', 'employee__user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'acknowledged_at']
    date_hierarchy = 'event_date'
    
    fieldsets = (
        ('Communication Details', {
            'fields': ('created_by', 'employee', 'log_type', 'subject', 'content')
        }),
        ('Event & Deadline', {
            'fields': ('event_date', 'requires_acknowledgment', 'acknowledgment_deadline', 'visibility')
        }),
        ('Acknowledgment Status', {
            'fields': ('is_acknowledged', 'acknowledged_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LogResponse)
class LogResponseAdmin(admin.ModelAdmin):
    list_display = ['communication_log', 'responder', 'created_at']
    list_filter = ['created_at']
    search_fields = ['response_text', 'responder__user__first_name', 'responder__user__last_name']
    readonly_fields = ['created_at', 'updated_at']
