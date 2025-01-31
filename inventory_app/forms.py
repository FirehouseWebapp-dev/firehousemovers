from django import forms
from gift.models import Employee
from .models import  UniformCatalog,Inventory,UniformAssignment,InventoryTransaction


class UniformCatalogForm(forms.ModelForm):

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            'rows':2,

        }),
        required=True
    )
    category = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            'rows':2,

        }),
        required=True
    )
    gender = forms.ChoiceField(
        choices=[("Male", "Male"), ("Female", "Female"), ("Unisex", "Unisex")],
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        })
    )
    minimum_stock_level = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )

    class Meta:
        model = UniformCatalog
        fields = ['name', 'category', 'gender', 'minimum_stock_level']


class UniformIssueForm(forms.ModelForm):

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select an Employee"
    )
    uniform = forms.ModelChoiceField(
        queryset=UniformCatalog.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select an Employee"
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )
    condition = forms.ChoiceField(
        choices=[("New", "New"), ("Used", "Used")],
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        })
    )
    
    class Meta:
        model = UniformAssignment
        fields = ['employee', 'uniform', 'quantity', 'condition']


class AddEmployeeForm(forms.ModelForm):
    DESIGNATION_CHOICES = [
            ('llc/field', 'LLC/Field'),
            ('llc/owner', 'LLC/Owner'),
            ('sales', 'Sales'),
            ('field', 'Field'),
            ('driver', 'Driver'),
            ('manager', 'Manager'),
            ('rwh', 'RWH'),
            ('admin', 'Admin'),
            ('warehouse', 'Warehouse'),
            ('mover', 'Mover'),
            ('mover- crew member', 'Mover- Crew member'),
            ('customers- per trevor', 'Customers- Per Trevor'),
        ]

    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            'rows':2,

        }),
        required=True
    )
    gender = forms.ChoiceField(
        choices=[("male", "Male"), ("female", "Female"), ("unisex", "Unisex")],
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        })
    )
    designation = forms.ChoiceField(
        choices=DESIGNATION_CHOICES,
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        })
    )

    class Meta:
        model = Employee
        fields = ['name', 'gender', 'designation']


class InventoryForm(forms.ModelForm):

    uniform = forms.ModelChoiceField(
        queryset=UniformCatalog.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        empty_label="Select a Uniform"
    )
    quantity = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        })
    )
    condition = forms.ChoiceField(
        choices=[("New", "New"), ("Used", "Used")],
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        })
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            'rows':1,

        }),
        required=False
    )
    transaction_type = forms.ChoiceField(
        choices=[
            ("Return to Supplier", "Return to Supplier"),
            ("Dispose", "Dispose"),
        ],
        widget=forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 w-full focus:outline-none focus:ring-2 focus:ring-red-500",
        }),
        required=False
    )
    class Meta:
        model = Inventory
        fields = ['uniform', 'quantity', 'condition','notes','transaction_type']
