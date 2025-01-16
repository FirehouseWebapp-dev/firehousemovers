from django import forms
from vehicle.models import Vehicle
from .models import Fleet_order, Trailer_inspection, Truck_inspection, Vehicle_inspection,Station_inspection

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


class TrailerInspectionForm(forms.ModelForm):
    class Meta:
        model = Trailer_inspection
        fields = [
            'date', 'trailer', 'clean_status', 'trash', 
            'blanket_84', 'hand_trucks_with_covers', 'four_wheel_dolly', 
            'short_straps', 'long_straps', 'ramp', 'rubber_bands', 
            'red_floor_runner', 'forearm_straps', 'wardrobe_boxes_with_bars', 
            'tv_box_for_rental', 'multi_tool_set', 'hand_tools_bag', 
            'two_carabiner', 'broom'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'type': 'date',
            }),
            'trailer': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'clean_status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'trash': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'blanket_84': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'hand_trucks_with_covers': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'four_wheel_dolly': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'short_straps': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'long_straps': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'ramp': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'rubber_bands': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'red_floor_runner': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'forearm_straps': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'wardrobe_boxes_with_bars': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'tv_box_for_rental': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'multi_tool_set': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'hand_tools_bag': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'two_carabiner': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'broom': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'saved_by': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            })
        }


class TruckInspectionForm(forms.ModelForm):
    class Meta:
        model = Truck_inspection
        fields = [
            'date', 'truck', 'clean_status', 'in_cab', 'bed_of_truck', 
            'first_aid_kit', 'floor_mats', 'business_cards', 'business_cards_magnetic', 
            'fuses', 'two_pens', 'sharpie', 'camera', 'flash_light', 'sun_visor', 
            'geo_tab', 'jack_and_links', 'cab_card', 'registration', 'insurance_card', 
            'accident_report_form', 'process_of_accident', 'fire_extinguisher', 
            'expiry_date_fe', 'four_way', 'min_7_orange', 'hazard_triangle_x3', 
            'jumper_cables', 'large_door_stops', 'trash_bag', 'roll_paper_towels', 
            'small_hand', 'bottle_jack', 'cones', 'spare_tire', 'condition_spare_tyre'
        ]
        widgets = {
            'date': forms.DateInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'type': 'date',
            }),
            'truck': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'clean_status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'in_cab': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'bed_of_truck': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'first_aid_kit': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'floor_mats': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'business_cards': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'business_cards_magnetic': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'fuses': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'two_pens': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'sharpie': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'camera': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'flash_light': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'sun_visor': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'geo_tab': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'jack_and_links': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'cab_card': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'registration': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'insurance_card': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'accident_report_form': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'process_of_accident': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'fire_extinguisher': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'expiry_date_fe': forms.DateInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
                'type': 'date',
            }),
            'four_way': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'min_7_orange': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'hazard_triangle_x3': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'jumper_cables': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'large_door_stops': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'trash_bag': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'roll_paper_towels': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'small_hand': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'bottle_jack': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'cones': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'spare_tire': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'condition_spare_tyre': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            })
        }