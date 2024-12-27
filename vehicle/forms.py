from django import forms
from .models import AvailabilityData, Dispatch,Order, Vehicle

class TruckAvailabilityForm(forms.ModelForm):
    class Meta:
        model = AvailabilityData
        fields = ['vehicle', 'status', 'estimated_back_in_service_date', 'back_in_service_date']
        widgets = {
            'estimated_back_in_service_date': forms.DateInput(attrs={'type': 'date'}),
            'back_in_service_date': forms.DateInput(attrs={'type': 'date'}),
        }



class OrderForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "placeholder": "Select date",
            }
        ),
        label="Date",
    )
    job_no = forms.CharField(
        max_length=20,
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "placeholder": "e.g., 12345 or 123456-7",
            }
        ),
        label="Job Number",
    )
    last_name_customer = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "placeholder": "Last name",
            }
        ),
        label="Last name",
    )
    phone_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "placeholder": "123-456-7890",
            }
        ),
        label="Phone Number",
    )
    type_of_move = forms.ChoiceField(
        choices=[("local", "Local"), ("long_distance", "Long Distance")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Type of Move",
    )
    moved_before = forms.ChoiceField(
        choices=[(True, "Yes"), (False, "No")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Moved Before",
    )
    crew_name = forms.ChoiceField(
        choices=[("n/a", "N/A"), ("chris", "Chris")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Crew Name",
    )
    referral_source = forms.ChoiceField(
        choices=[("google", "Google"), ("referral", "Referral"), ("other", "Other")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Referral Source",
    )

    crew_available = forms.ChoiceField(
        choices=[(True, "Yes"), (False, "No")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Crew Available",
    )
    number_of_trucks = forms.ChoiceField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Number of Trucks Required",
    )
    number_of_trailers = forms.ChoiceField(
        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Number of Trailers Required",
    )
    notes_order_detail = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "rows": 1,
                "placeholder": "Enter additional notes...",
            }
        ),
        label="Order Notes",
        required=False,
    )

    class Meta:
        model = Order
        fields = [
            "date",
            "job_no",
            "phone_number",
            "type_of_move",
            "moved_before",
            "crew_name",
            "referral_source",
            "crew_available",
            "number_of_trucks",
            "number_of_trailers",
            "notes_order_detail",
            "last_name_customer"
        ]


class DispatchForm(forms.ModelForm):
    ipad = forms.ChoiceField(
        choices=[("iPad 1", "iPad 1"), ("iPad 2", "iPad 2"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="iPad#",
    )
    crew_leads = forms.ChoiceField(
        choices=[("Lead 1", "Lead 1"), ("Lead 2", "Lead 2"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Crew Leads",
    )
    drivers = forms.ChoiceField(
        choices=[("Driver 1", "Driver 1"), ("Driver 2", "Driver 2"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Drivers",
    )
    truck_1 = forms.ChoiceField(
        choices=[(truck.id, truck.name) for truck in Vehicle.objects.filter(vehicle_type='truck')],

        # choices=[],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Truck 1",
    )
    truck_2 = forms.ChoiceField(
        required=False,
        choices=[("Truck A", "Truck A"), ("Truck B", "Truck B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Truck 2",
    )
    truck_3 = forms.ChoiceField(
        required=False,
        choices=[("Truck A", "Truck A"), ("Truck B", "Truck B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Truck 3",
    )
    truck_4 = forms.ChoiceField(
        required=False,
        choices=[("Truck A", "Truck A"), ("Truck B", "Truck B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Truck 4",
    )
    trailer_1 = forms.ChoiceField(
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Trailer 1",
    )
    trailer_2 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Trailer 2",
    )
    trailer_3 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Trailer 3",
    )
    trailer_4 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Trailer 4",
    )

    material = forms.ChoiceField(
        choices=[("Material A", "Material A"), ("Material B", "Material B"), ("None", "None")],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Material",
    )
    special_equipment_needed = forms.ChoiceField(
        choices=[
            ("Equipment A", "Equipment A"),
            ("Equipment B", "Equipment B"),
            ("None", "None"),
        ],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Special Equipment Needed",
    )
    special_equipment_status = forms.ChoiceField(
        choices=[
            ("Operational", "Operational"),
            ("Out of Service", "Out of Service"),
            ("Pending", "Pending"),
        ],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Special Equipment Status",
    )
    speedy_inventory_account = forms.ChoiceField(
        choices=[
            ("Account A", "Account A"),
            ("Account B", "Account B"),
            ("None", "None"),
        ],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Speedy Inventory Account",
    )
    speedy_inventory = forms.ChoiceField(
        choices=[
            ("Inventory A", "Inventory A"),
            ("Inventory B", "Inventory B"),
            ("None", "None"),
        ],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Speedy Inventory",
    )
    labels_for_speedy_inventory = forms.ChoiceField(
        choices=[
            ("Label A", "Label A"),
            ("Label B", "Label B"),
            ("None", "None"),
        ],
        widget=forms.Select(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            }
        ),
        label="Labels for Speedy Inventory",
    )
    notes_dispatcher = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
                "rows": 3,
                "placeholder": "Enter dispatch notes...",
            }
        ),
        label="Dispatch Notes",
    )

    class Meta:
        model = Dispatch
        fields = [
            "ipad",
            "crew_leads",
            "drivers",
            "truck_1",
            "trailer_1",
            "truck_2",
            "trailer_2",
            "truck_3",
            "trailer_3",
            "truck_4",
            "trailer_4",
            "material",
            "special_equipment_needed",
            "special_equipment_status",
            "speedy_inventory_account",
            "speedy_inventory",
            "labels_for_speedy_inventory",
            "notes_dispatcher",
        ]


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # Fetch all trucks and trailers from the Vehicle model
    #     trucks = Vehicle.objects.filter(vehicle_type='truck')
    #     trailers = Vehicle.objects.filter(vehicle_type='trailer')

    #     truck_choices = [(truck.name, truck.name) for truck in trucks]
    #     truck_choices.append((None, "None"))

    #     trailer_choices = [(trailer.name, trailer.name) for trailer in trailers]
    #     trailer_choices.append((None, "None"))

    #     # Assign the same dynamic choices for all truck and trailer fields
    #     for i in range(1, 5):  # Adjust the range if you have more fields
    #         self.fields[f'truck_{i}'].choices = truck_choices
    #         self.fields[f'trailer_{i}'].choices = trailer_choices
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch all trucks and trailers from the Vehicle model
        trucks = Vehicle.objects.filter(vehicle_type='truck')
        trailers = Vehicle.objects.filter(vehicle_type='trailer')

        # Set choices to use the ID as the value and name for display
        truck_choices = [(truck.id, truck.name) for truck in trucks]
        trailer_choices = [(trailer.id, trailer.name) for trailer in trailers]

        # Assign the dynamic choices for all truck and trailer fields
        for i in range(1, 5):  # Adjust the range if you have more fields
            self.fields[f'truck_{i}'].choices = truck_choices
            self.fields[f'trailer_{i}'].choices = trailer_choices


