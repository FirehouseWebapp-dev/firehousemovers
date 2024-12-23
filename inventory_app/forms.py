from django import forms
from .models import Inventory, Employee, UniformAssignment


class InventoryForm(forms.ModelForm):
    """Form for managing inventory items."""
    class Meta:
        model = Inventory
        fields = "__all__"


class EmployeeForm(forms.ModelForm):
    """Form for managing employee data."""
    class Meta:
        model = Employee
        fields = "__all__"


class UniformAssignmentForm(forms.ModelForm):
    """Form for assigning uniforms to employees."""
    class Meta:
        model = UniformAssignment
        fields = "__all__"
