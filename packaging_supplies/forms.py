from django import forms
from .models import Material, OrderReceipt
from vehicle.models import Vehicle
from authentication.models import UserProfile

class BaseMaterialForm(forms.ModelForm):
    trailer_number = forms.ModelChoiceField(
        queryset=Vehicle.objects.filter(vehicle_type='trailer'),
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
        })
    )
    employee = forms.ModelChoiceField(
        queryset=UserProfile.objects.exclude(role="admin"),
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
        })
    )
    
    # Material fields with common attributes
    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user:
            self.fields['employee'].queryset = UserProfile.objects.exclude(user=current_user).exclude(role="admin")
        else:
            self.fields['employee'].queryset = UserProfile.objects.exclude(role="admin")
        for field_name in self.fields:
            if field_name not in ['job_id', 'trailer_number', 'employee', 'employee_signature']:
                self.fields[field_name].widget.attrs.update({
                    "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                    "min": "0"
                })

class PullMaterialForm(BaseMaterialForm):
    job_id = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
        })
    )

    class Meta:
        model = Material
        fields = [
            'job_id', 'trailer_number', 'employee',
            'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
            'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
            'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
            'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
            'packing_peanuts', 'ram_board', 'mattress_bags',
            'mirror_cartons', 'bubble_wrap', 'gondola_boxes',
            'employee_signature'
        ]
        widgets = {
            'employee_signature': forms.TextInput(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
            })
        }

class ReturnMaterialForm(BaseMaterialForm):
    job_id = forms.ChoiceField(
        choices=[],
        required=True,
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get unique job_ids from pull transactions
        job_ids = Material.objects.filter(transaction_type='pull').values_list('job_id', flat=True).distinct()
        # Add blank choice at the top
        self.fields['job_id'].choices = [('', '---------')] + [(job_id, job_id) for job_id in job_ids]
        
        # Make fields required
        self.fields['trailer_number'].required = True
        self.fields['employee_signature'].required = True

    class Meta:
        model = Material
        fields = [
            'job_id', 'trailer_number', 'employee',
            'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
            'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
            'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
            'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
            'packing_peanuts', 'ram_board', 'mattress_bags',
            'mirror_cartons', 'bubble_wrap', 'gondola_boxes',
            'employee_signature'
        ]
        widgets = {
            'employee_signature': forms.TextInput(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "required": "required"
            }),
            'trailer_number': forms.Select(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "required": "required"
            })
        }

class OrderMaterialForm(BaseMaterialForm):
    job_id = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
        })
    )
    
    supplier_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            "placeholder": "Enter supplier's email address"
        })
    )

    class Meta:
        model = Material
        fields = [
            'job_id', 'trailer_number', 'employee',
            'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
            'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
            'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
            'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
            'packing_peanuts', 'ram_board', 'mattress_bags',
            'mirror_cartons', 'bubble_wrap', 'gondola_boxes',
            'employee_signature'
        ]
        widgets = {
            'employee_signature': forms.TextInput(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
            })
        }

class OrderReceiptForm(forms.ModelForm):
    class Meta:
        model = OrderReceipt
        fields = ['date_received']
        widgets = {
            'date_received': forms.DateInput(attrs={
                'type': 'date',
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full"
            })
        }
