from django import forms
from .models import Inventory, Employee, UniformAssignment
from django.contrib.auth.forms import UserCreationForm
from inventory_app.models import User


class SignUpForm(UserCreationForm):  
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "First name",
                "style": "border-radius: 5px; padding: 10px;"
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Last name",
                "style": "border-radius: 5px; padding: 10px;"
            }
        ),
    )
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "Email",
                "id": "id_email",
                "style": "border-radius: 5px; padding: 10px;"
            }
        ),
    )
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('driver', 'Driver')],
        widget=forms.Select(attrs={
            "class": "form-control",
            "style": "border-radius: 5px; padding: 10px;"
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
                "style": "border-radius: 5px; padding: 10px;"
            }
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Repeat password",
                "style": "border-radius: 5px; padding: 10px;"
            }
        ),
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "role",
            "password1",
            "password2",
        )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Password does not match")
        return cleaned_data


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
