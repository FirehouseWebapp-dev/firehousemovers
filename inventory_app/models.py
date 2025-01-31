from django.db import models
from gift.models import Employee



class UniformCatalog(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=20, choices=[("Male", "Male"), ("Female", "Female"), ("Unisex", "Unisex")], null=True, blank=True)
    minimum_stock_level = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class UniformAssignment(models.Model):
    date = models.DateField(null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)
    uniform = models.ForeignKey(UniformCatalog, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    condition = models.CharField(max_length=10, choices=[("New", "New"), ("Used", "Used")], null=True, blank=True)
    status = models.CharField(max_length=20, choices=[("Active", "Active"), ("Returned", "Returned")], null=True, blank=True)

    def __str__(self):
        return f"{self.uniform.name} assigned to {self.employee.name}"


class Inventory(models.Model):
    uniform = models.ForeignKey(UniformCatalog, on_delete=models.CASCADE, null=True, blank=True)
    new_stock = models.PositiveIntegerField(null=True, blank=True)
    used_stock = models.PositiveIntegerField(null=True, blank=True, default=0)
    total_stock = models.PositiveIntegerField(editable=False, null=True, blank=True)  # Auto-calculated
    in_use = models.PositiveIntegerField(null=True, blank=True)
    disposed = models.PositiveIntegerField(null=True, blank=True, default=0)
    return_to_supplier = models.PositiveIntegerField(null=True, blank=True, default=0)
    total_bought = models.PositiveIntegerField(editable=False, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Safely sum the stock values, treating None as 0
        self.total_stock = (self.new_stock if self.new_stock is not None else 0) + \
                        (self.used_stock if self.used_stock is not None else 0) + \
                        (self.in_use if self.in_use is not None else 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.uniform.name} - Inventory"
    

class InventoryTransaction(models.Model):
    date = models.DateTimeField(null=True, blank=True)
    transaction_type = models.CharField(max_length=50, choices=[
        ("Purchase", "Purchase"),
        ("Return to Supplier", "Return to Supplier"),
        ("Dispose", "Dispose"),
    ], null=True, blank=True)
    uniform = models.ForeignKey(UniformCatalog, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    condition = models.CharField(max_length=10, choices=[("New", "New"), ("Used", "Used")], null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.uniform.name}"

