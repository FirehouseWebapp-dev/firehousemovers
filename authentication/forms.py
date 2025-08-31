from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import UserProfile, Department
from django.db.models import Q

import re

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": " bg-custom-dark rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "First name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": " bg-custom-dark rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Last name",
            }
        ),
    )
    email = forms.EmailField(
        max_length=150,
        widget=forms.EmailInput(
            attrs={
                "class": "bg-custom-dark rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Email",
                "id": "id_email",
            }
        ),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "bg-custom-dark rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Password",
            }
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": " bg-custom-dark rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Repeat password",
            }
        ),
    )
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "password1",
            "password2",
        )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Password does not match")
        return cleaned_data

    def clean_profile_picture(self):
        picture = self.cleaned_data.get("profile_picture")
        if picture:
            if picture.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image file too large (max 5MB).")
            if not picture.content_type.startswith("image/"):
                raise ValidationError("Only image files are allowed.")
        return picture

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email Address",
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Email address",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
                "placeholder": "Password",
            }
        ),
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        try:
            user = get_user_model().objects.get(email=username)
        except get_user_model().DoesNotExist:
            raise forms.ValidationError("User with this email does not exist.")
        return user

class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )

    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )

    role = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )

    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )

    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )

    hobbies = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2",
            "rows": 3
        })
    )

    favourite_quote = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2",
            "rows": 3
        })
    )

    profile_picture = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            "class": "w-full bg-black border border-gray-600 rounded px-3 py-2 text-white mt-2"
        })
    )

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email',  # proxy from User
            'phone_number', 'role', 'location',
            'start_date', 'profile_picture',
            'hobbies', 'favourite_quote',
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.fields['role'].disabled = True
        self.fields['start_date'].disabled = True
        self.fields['profile_picture'].required = False

        if user and isinstance(user, User):
            # Populate initial values from User model
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email


    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user

        user.first_name = self.cleaned_data['first_name'].capitalize()
        user.last_name = self.cleaned_data['last_name'].capitalize()
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            profile.save()
        return profile

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number")
        if phone:
            import re
            pattern = re.compile(r'^(?:\+1\s?)?(?:\(?\d{3}\)?[\s.-]?)?\d{3}[\s.-]?\d{4}$')
            if not pattern.match(phone):
                raise ValidationError("Enter a valid US phone number.")
        return phone

from django.contrib.auth.forms import PasswordChangeForm

class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "w-full bg-black border border-gray-600 text-white rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-red-500"
            })


class AddTeamMemberForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Will be set in __init__
        label="Select User",
        widget=forms.Select(attrs={
            "class": "w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
        })
    )
    role = forms.ChoiceField(
        choices=UserProfile.EMPLOYEE_CHOICES,
        widget=forms.Select(attrs={
            "class": "w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-600 text-white"
        })
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-600 text-white"
        })
    )

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if current_user:
            self.fields['user'].queryset = User.objects.filter(
                is_active=True,  
                userprofile__isnull=False,
                userprofile__manager__isnull=True,  
            ).exclude(
                pk=current_user.pk  
            ).exclude(
                userprofile__role__in=['admin', 'manager']  
            )

        self.fields['user'].label_from_instance = lambda obj: obj.get_full_name() or obj.username

class TeamMemberEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role', 'start_date']
        widgets = {
            'role': forms.Select(attrs={
                "class": "w-full bg-gray-800 border border-gray-600 text-white rounded px-3 py-2"
            }),
            'start_date': forms.DateInput(attrs={
                "type": "date",
                "class": "w-full bg-gray-800 border border-gray-600 text-white rounded px-3 py-2"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].label = "Assign Role"
        self.fields['start_date'].label = "Set Start Date"

User = get_user_model()


class DepartmentForm(forms.ModelForm):
    employees = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.select_related("user").order_by("user__username"),
        required=False,
    )

    class Meta:
        model = Department
        fields = ["title", "description", "manager"]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white",
                "placeholder": "Enter department title"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white",
                "rows": 3,
                "placeholder": "Enter department description"
            }),
            "manager": forms.Select(attrs={
                "class": "w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['employees'].label_from_instance = (
            lambda obj: obj.user.get_full_name() or obj.user.username
        )

        if self.instance and self.instance.pk:
            self.fields['employees'].initial = UserProfile.objects.filter(department=self.instance)

        base_manager_qs = UserProfile.objects.filter(role="manager")

        if self.instance and self.instance.pk and self.instance.manager_id:
            excluded = UserProfile.objects.filter(managed_department__isnull=False).exclude(id=self.instance.manager_id)
        else:
            excluded = UserProfile.objects.filter(managed_department__isnull=False)

        self.fields["manager"].queryset = base_manager_qs.exclude(id__in=excluded)

        self.fields['employees'].queryset = (
            UserProfile.objects.exclude(
                Q(is_admin=True) |
                Q(is_manager=True) |
                Q(is_senior_management=True)
            ).filter(
                Q(department__isnull=True) |
                Q(department=self.instance if self.instance.pk else None)
            ).select_related("user").order_by("user__username")
        )

    def clean(self):
        cleaned = super().clean()
        manager = cleaned.get("manager")
        employees = cleaned.get("employees") or []

        if manager and manager in employees:
            raise ValidationError("The selected manager cannot also be listed as an employee of the same department.")

        return cleaned
