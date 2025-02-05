from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    Employee_choices=[('llc/field', 'LLC/Field'),
        ('llc/owner', 'LLC/Owner'),
        ('sales', 'Sales'),
        ('field', 'Field'),
        ('driver', 'Driver'),
        ('manager', 'Manager'),
        ('rwh', 'RWH'),
        ('technician', 'Technician'),
        ('admin', 'Admin'),
        ('warehouse', 'Warehouse'),
        ('mover', 'Mover'),
        ('technician', 'Technician'),
        ('customers- per trevor', 'Customers- Per Trevor'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=Employee_choices, default='driver')

    def __str__(self):
        return self.user.username

