from django import forms
from authentication.models import UserProfile
from .models import Award, Gift_card, Gift_company, AwardCategory, HallOfFameEntry

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

class AwardForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['card'].required = False
        self.fields['amount'].required = False
        self.fields['employees'].label_from_instance = lambda obj: obj.user.get_full_name() if hasattr(obj, 'user') else str(obj)

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

class AwardCategoryForm(forms.ModelForm):
    class Meta:
        model = AwardCategory
        fields = ['name', 'description', 'criteria']
        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full bg-custom-dark text-white rounded-lg p-3 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            }),
            "description": forms.Textarea(attrs={
                "class": "w-full bg-custom-dark text-white rounded-lg p-3 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-red-500",
                "rows": 3,
                "placeholder": "Brief description of the award category..."
            }),
            "criteria": forms.Textarea(attrs={
                "class": "w-full bg-custom-dark text-white rounded-lg p-3 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-red-500",
                "rows": 3,
                "placeholder": "Criteria to win this award..."
            }),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        qs = AwardCategory.objects.filter(name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A category with this name already exists.")
        return name

    def clean_description(self):
        desc = self.cleaned_data.get('description', '')
        if desc and len(desc.strip()) < 10:
            raise forms.ValidationError("Description must be at least 10 characters long if provided.")
        return desc

    def clean_criteria(self):
        criteria = self.cleaned_data.get('criteria', '')
        if criteria and len(criteria.strip()) < 10:
            raise forms.ValidationError("Criteria must be at least 10 characters long if provided.")
        return criteria


class HallOfFameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["employee"].label_from_instance = lambda obj: obj.get_full_name() or obj.username

    class Meta:
        model = HallOfFameEntry
        fields = ['employee', 'description', 'photo']
        widgets = {
            "employee": forms.Select(attrs={
                "class": "w-full bg-custom-dark text-white rounded-lg p-3 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-red-500"
            }),
            "description": forms.TextInput(attrs={
                "class": "w-full bg-custom-dark text-white rounded-lg p-3 border border-gray-700 focus:outline-none focus:ring-2 focus:ring-red-500",
            }),
            "photo": forms.ClearableFileInput(attrs={"class": "hidden"}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if photo and hasattr(photo, "content_type") and not photo.content_type.startswith("image/"):
            raise forms.ValidationError("Only image files are allowed.")
        return photo

