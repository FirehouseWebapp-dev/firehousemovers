from django import forms
from vehicle.models import Vehicle
from .models import Fleet_order,Vehicle_inspection,Station_inspection


class StationInspectionForm(forms.ModelForm):
    class Meta:
        model = Station_inspection
        fields = [
            'back_lot_cleanliness', 'back_lot_maintenance',
            'front_yard_cleanliness', 'front_yard_landscaping',
            'inventory_status', 'missing_tools', 'tool_cleanliness',
            'tool_functionality', 'bathroom_cleanliness',
            'bathroom_maintenance', 'supplies', 'extinguisher_status',
            'emergency_exit_status', 'notes'
        ]
        widgets = {
            'station': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'back_lot_cleanliness': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'back_lot_maintenance': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'front_yard_cleanliness': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'front_yard_landscaping': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'inventory_status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'missing_tools': forms.Textarea( attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "rows": 1,
                "placeholder": "List missing tools",
            }),
            'tool_cleanliness': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'tool_functionality': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'bathroom_cleanliness': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'bathroom_maintenance': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'supplies': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'extinguisher_status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'emergency_exit_status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full h-32',
                'placeholder': 'Add any additional notes here...'
            }),
        }


class VehicleInspectionForm(forms.ModelForm):
    class Meta:
        model = Vehicle_inspection
        fields = ['type', 'vehicle', 'technician', 'date', 'description']
        widgets = {
            'type': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'vehicle': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'technician': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'date': forms.DateInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'type': 'date',
            }),
            'description': forms.Textarea(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "rows": 1,
                'placeholder': 'Enter description of the inspection...',
            }),
        }

    def __init__(self, *args, **kwargs):
        # Extract `vehicle_type` from kwargs and remove it
        vehicle_type = kwargs.pop('vehicle_type', None)
        super().__init__(*args, **kwargs)
        if vehicle_type:
            # Filter the vehicle queryset based on the provided `vehicle_type`
            self.fields['vehicle'].queryset = Vehicle.objects.filter(vehicle_type=vehicle_type)


class FleetOrderForm(forms.ModelForm):
    class Meta:
        model = Fleet_order
        fields = ['date', 'requested_by', 'item_description', 'quantity', 'urgency_level']
        
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'type': 'date',
                'placeholder': 'dd/mm/yyyy',
            }),
            'requested_by': forms.TextInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'placeholder': 'Enter the requester\'s name',
            }),
            'item_description': forms.Textarea(attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "rows": 1,
                "placeholder": "Enter Description of the item",
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'min': 1,
                'placeholder': 'Enter quantity',
            }),
            'urgency_level': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
        }

