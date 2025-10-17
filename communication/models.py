from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from authentication.models import UserProfile, Department


class LogType(models.Model):
    """Categories for communication logs"""
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='fa-comment', help_text='FontAwesome icon class')
    color = models.CharField(max_length=20, default='gray', help_text='Tailwind color name')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CommunicationLog(models.Model):
    """Communication logs between managers and employees"""
    
    VISIBILITY_CHOICES = [
        ('shared', 'Shared with Employee'),
        ('private', 'Private (Manager Only)'),
    ]
    
    # Who and What
    created_by = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='logs_created'
    )
    employee = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='logs_received'
    )
    log_type = models.ForeignKey(
        LogType,
        on_delete=models.SET_NULL,
        null=True,
        related_name='logs'
    )
    
    # Content
    subject = models.CharField(max_length=200)
    content = models.TextField(help_text='Detailed notes about the communication')
    
    # Visibility and Status
    visibility = models.CharField(
        max_length=10,
        choices=VISIBILITY_CHOICES,
        default='shared'
    )
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Event tracking
    event_date = models.DateField(
        default=timezone.now,
        help_text='Date when the event/incident occurred'
    )
    
    # Acknowledgment tracking
    requires_acknowledgment = models.BooleanField(
        default=True,
        help_text='Whether employee needs to acknowledge this log'
    )
    acknowledgment_deadline = models.DateField(
        null=True, 
        blank=True,
        help_text='Deadline for employee to acknowledge this log'
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_by', 'employee']),
            models.Index(fields=['employee', 'is_acknowledged']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.employee.user.get_full_name()}"

    def acknowledge(self):
        """Mark log as acknowledged"""
        self.is_acknowledged = True
        self.acknowledged_at = timezone.now()
        self.save()


class LogResponse(models.Model):
    """Employee responses to communication logs"""
    communication_log = models.ForeignKey(
        CommunicationLog,
        on_delete=models.CASCADE,
        related_name='responses'
    )
    responder = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='log_responses'
    )
    response_text = models.TextField()
    viewed_by_senior = models.BooleanField(
        default=False,
        help_text="Whether senior manager has viewed this response"
    )
    viewed_by_manager = models.BooleanField(
        default=False,
        help_text="Whether manager has viewed this response"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Response by {self.responder} on {self.created_at}"
