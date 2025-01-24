from django import forms
from .models import Award, Employee, Gift_card, Gift_company
from django.core.exceptions import ValidationError


class GiftCardForm(forms.ModelForm):
    date_of_purchase = forms.DateField(
        input_formats=['%d/%m/%Y'],  # This is your expected input format
        widget=forms.TextInput(attrs={
            'placeholder': 'DD/MM/YYYY',  # Use a text input with a placeholder
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )
    amount = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )
    company = forms.ModelChoiceField(
        queryset=Gift_company.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select a Company"
    )

    class Meta:
        model = Gift_card
        fields = ['company', 'date_of_purchase', 'amount']

    def clean(self):
        cleaned_data = super().clean()  # Get the cleaned data

        # Access the fields' cleaned data
        amount = cleaned_data.get('amount')
        if amount is not None and amount < 1:
            self.add_error('amount', f"The Gift Card amount cannot be less than one ({amount}).")

        return cleaned_data


class AwardCardForm(forms.ModelForm):
    date_award = forms.DateField(
        input_formats=['%d/%m/%Y'], 
        widget=forms.DateInput(attrs={
            'placeholder': 'DD/MM/YYYY',
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )
    employee_name = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select an Employee"
    )
    company_name = forms.ModelChoiceField(
        queryset=Gift_company.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select a Company"
    )
    amount = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )
    card = forms.ModelChoiceField(
        queryset=Gift_card.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select a Card"
    )
    reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            'placeholder': 'Reason for Gift Given',
            'rows':2,

        }),
        required=True
    )

    class Meta:
        model = Award
        fields = ['date_award', 'employee_name', 'company_name', 'amount', 'card', 'reason']