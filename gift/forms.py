from django import forms
from authentication.models import UserProfile
from .models import Award, Gift_card, Gift_company


class GiftCardForm(forms.ModelForm):
    amount = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
            }
        )
    )
    company = forms.ModelChoiceField(
        queryset=Gift_company.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
            }
        ),
        empty_label="Select a Company",
    )

    class Meta:
        model = Gift_card
        fields = ["company", "amount"]

    def clean(self):
        cleaned_data = super().clean()  # Get the cleaned data

        # Access the fields' cleaned data
        amount = cleaned_data.get("amount")
        if amount is not None and amount < 1:
            self.add_error(
                "amount", f"The Gift Card amount cannot be less than one ({amount})."
            )

        return cleaned_data


class AwardCardForm(forms.ModelForm):
    employees = forms.SelectMultiple(
        choices=[(user.id, user.user) for user in UserProfile.objects.all()],
        attrs={"class": "form-select"},
    )
    card = forms.ModelChoiceField(
        queryset=Gift_card.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
            }
        ),
        empty_label="Select a Card",
    )
    reason = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "placeholder": "Reason for Gift Given",
                "rows": 2,
            }
        ),
        required=True,
    )

    class Meta:
        model = Award
        fields = [
            "employees",
            "card",
            "reason",
        ]

# awards/forms.py

class AwardForm(forms.ModelForm):
    class Meta:
        model = Award
        fields = ['category', 'employees', 'card', 'amount', 'employee_photo', 'reason']
        widgets = {
            "category": forms.Select(attrs={"class": "w-full choices__inner text-white rounded-lg p-3 border border-gray-600"}),
            "employees": forms.Select(attrs={"class": "w-full choices__inner text-white rounded-lg p-3"}),
            "card": forms.Select(attrs={"class": "w-full choices__inner text-white rounded-lg p-3"}),
            "amount": forms.NumberInput(attrs={"class": "w-full choices__inner text-white rounded-lg p-3"}),
            "reason": forms.Textarea(attrs={"class": "w-full choices__inner text-white rounded-lg p-3 border border-gray-600", "rows": 3}),

        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['card'].required = False
        self.fields['amount'].required = False

    def clean_employee_photo(self):
        photo = self.cleaned_data.get("employee_photo")
        if photo and hasattr(photo, "content_type"):
            if not photo.content_type.startswith("image/"):
                raise forms.ValidationError("Only image files are allowed.")
        return photo
    
    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        card = cleaned_data.get("card")
        amount = cleaned_data.get("amount")

        if category and category.name == "gift_card":
            if not card:
                self.add_error("card", "This field is required for Gift Card awards.")
            if not amount:
                self.add_error("amount", "This field is required for Gift Card awards.")

        return cleaned_data

from .models import AwardCategory

class AwardCategoryForm(forms.ModelForm):
    class Meta:
        model = AwardCategory
        fields = ['name']
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full bg-custom-dark text-white rounded-lg p-3 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            })
        }

    def clean_name(self):
        name = self.cleaned_data['name']
        if AwardCategory.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name
