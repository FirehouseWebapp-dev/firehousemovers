from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model


class SignUpForm(UserCreationForm):  
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "First name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Last name",
            }
        ),
    )
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Email",
                "id": "id_email",
            }
        ),
    )
    role = forms.ChoiceField(
        choices=[('manager', 'Manager'), ('driver', 'Driver')],
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Repeat password",
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
        


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='Email Address',
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Email address",
            }
        ),
    )

    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Password",
            }
        ),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        try:
            user = get_user_model().objects.get(email=username)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError("User with this email does not exist.")
        return user
