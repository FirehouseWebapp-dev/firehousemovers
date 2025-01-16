from django.db import models

class Inventory(models.Model):
    name = models.CharField(max_length=255,null=True, blank=True)
    category = models.CharField(max_length=255,null=True, blank=True)
    gender = models.CharField(max_length=50,null=True, blank=True)
    minimum_stock = models.IntegerField(null=True, blank=True)
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
    name = models.CharField(max_length=255,null=True, blank=True)
    gender = models.CharField(max_length=50,null=True, blank=True)
    designation = models.CharField(max_length=255,null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('inactive', 'Inactive')], default='active')

    def __str__(self):
        return self.name


class InventoryAssignment(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,null=True, blank=True)
    uniform = models.ForeignKey(Inventory, on_delete=models.CASCADE,null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    condition = models.CharField(max_length=50, choices=[('new', 'New'), ('used', 'Used')],null=True, blank=True)
    date_assigned = models.DateField(auto_now_add=True,null=True, blank=True)
    status = models.CharField(max_length=50, choices=[('active', 'Active'), ('returned', 'Returned')], default='active',null=True, blank=True)

    def __str__(self):
        return f"{self.employee.name} - {self.uniform.name} ({self.quantity})"

