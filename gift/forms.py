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
