from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[('manager', 'Manager'), ('driver', 'Driver')], default='driver')

    def __str__(self):
        return self.user.username


class Inventory(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255)
    gender = models.CharField(max_length=50)
    minimum_stock = models.IntegerField()
    new_stock = models.IntegerField(default=0)
    used_stock = models.IntegerField(default=0)
    in_use = models.IntegerField(default=0)
    disposed = models.IntegerField(default=0)
    not_returned = models.IntegerField(default=0)
    return_to_supplier = models.IntegerField(default=0)

    def total_stock(self):
        """Calculate total stock as the sum of new, used, and in-use items."""
        return self.new_stock + self.used_stock + self.in_use

    def total_bought(self):
        """Calculate total bought as disposed + not returned + in use - returned to supplier."""
        return self.disposed + self.not_returned + self.in_use - self.return_to_supplier

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = "Inventory"
        verbose_name_plural = "Inventories"


class Employee(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=50)
    designation = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.name


class UniformAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    uniform = models.ForeignKey(Inventory, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    condition = models.CharField(max_length=50, choices=[('new', 'New'), ('used', 'Used')])
    date_assigned = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('returned', 'Returned')], default='active')

    def __str__(self):
        return f"{self.employee.name} - {self.uniform.name} ({self.quantity})"

