from django.db.models import Prefetch
from django import forms
from authentication.models import UserProfile
from .models import AvailabilityData, Crew, Dispatch,Order, Vehicle
from django.db.models import Prefetch
from django.db.models import Max, Subquery



class TruckAvailabilityForm(forms.ModelForm):
    class Meta:
        model = AvailabilityData
        fields = ['vehicle', 'status', 'estimated_back_in_service_date', 'back_in_service_date']
        widgets = {
            'vehicle': forms.TextInput(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'status': forms.Select(attrs={
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'estimated_back_in_service_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
            'back_in_service_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full',
            }),
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
        choices = [
            ("moving", "Moving"),
            ("packing", "Packing"),
            ("moving_packing", "Moving & Packing"),
            ("load_only", "Load Only"),
            ("unload_only", "Unload Only"),
            ("commercial", "Commercial"),
            ("storage_inbound", "Storage Inbound"),
            ("storage_outbound", "Storage Outbound"),
            ("inner_house", "Inner House"),
            ("junk_removal", "Junk Removal"),
            ("unpacking", "Unpacking"),
            ("pack_load", "Pack & Load")
        ],

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
    crew_name = forms.ModelChoiceField(
        queryset=Crew.objects.all(),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        label="Crew Name",
    )
    referral_source = forms.ChoiceField(
        choices = [
            ("moved_before", "Moved Before"),
            ("friend", "Friend"),
            ("fire_station", "Fire Station"),
            ("realtor_referral", "Realtor Referral"),
            ("is_a_realtor", "Is a Realtor"),
            ("way_fm", "Way FM"),
            ("yelp", "Yelp"),
            ("google", "Google"),
            ("angis", "Angi's"),
            ("saw_truck", "Saw Truck"),
            ("facebook", "Facebook"),
            ("mailers", "Mailers"),
            ("elevate_life_church", "Elevate Life Church"),
            ("nikki_brian", "Nikki & Brian"),
            ("cb_jeni_homes", "CB Jeni Homes"),
            ("drive_by", "Drive By"),
            ("next_door", "Next Door"),
            ("century_21_judge_fite_concierge", "Century 21 Judge Fite Concierge"),
            ("bbb", "BBB"),
            ("the_wolf_99_5", "The Wolf 99.5"),
            ("the_ticket_radio", "The Ticket Radio"),
            ("great_guy_movers", "Great Guy Movers"),
            ("the_good_contractors_list", "The Good Contractors List"),
            ("trinity_floors", "Trinity Floors"),
            ("highland_springs", "Highland Springs"),
            ("rohail", "Rohail")
        ],

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
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="iPad#",
    )
    crew_leads = forms.ModelChoiceField(
        queryset=Crew.objects.filter(role='leader'),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        label="Crew Leads",
    )
    drivers = forms.ModelChoiceField(
        queryset=UserProfile.objects.filter(role='driver'),
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full'
        }),
        label="Drivers",
    )
    truck_1 = forms.ChoiceField(
        required=False,
        choices=[(truck.id, truck.name) for truck in Vehicle.objects.filter(vehicle_type='truck')],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Truck 1",
    )
    truck_2 = forms.ChoiceField(
        required=False,
        choices=[("Truck A", "Truck A"), ("Truck B", "Truck B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Truck 2",
    )
    truck_3 = forms.ChoiceField(
        required=False,
        choices=[("Truck A", "Truck A"), ("Truck B", "Truck B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Truck 3",
    )
    truck_4 = forms.ChoiceField(
        required=False,
        choices=[("Truck A", "Truck A"), ("Truck B", "Truck B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Truck 4",
    )
    trailer_1 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Trailer 1",
    )
    trailer_2 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Trailer 2",
    )
    trailer_3 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Trailer 3",
    )
    trailer_4 = forms.ChoiceField(
        required=False,
        choices=[("Trailer A", "Trailer A"), ("Trailer B", "Trailer B"), ("None", "None")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Trailer 4",
    )
    material = forms.ChoiceField(
        required=False,
        choices=[("Loaded in Trailer", "Loaded in Trailer"), ("Pulled", "Pulled"), ("Needed to Pull", "Needed to Pull"),("Not Required", "Not Required")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Material",
    )
    special_equipment_needed = forms.ChoiceField(
        required=False,
        choices=[("No", "No"), ("Dolly", "Dolly"), ("Hydraulic Stair Climber Dolly", "Hydraulic Stair Climber Dolly"),
                 ("Piano Board And Moon Dog", "Piano Board And Moon Dog"),("Monter 4 Wheel Dolly", "Monter 4 Wheel Dolly"),
                 ("Red Panel Cart", "Red Panel Cart"),("Yellow Off Road Panel Card","Yellow Off Road Panel Card"),
                 ("Snap Lock Dollies", "Snap Lock Dollies")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Special Equipment Needed",
    )
    special_equipment_status = forms.ChoiceField(
        required=False,
        choices=[(None, "N/A"),("Needs Staged","Needs Staged"), ("In Staging Area","In Staging Area"), ("Loaded", "Loaded")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Special Equipment Status",
    )
    speedy_inventory_account = forms.ChoiceField(
        required=False,
        choices=[("No", "No"), ("Needed", "Needed"), ("Comleted", "Comleted")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Speedy Inventory Account",
    )
    speedy_inventory = forms.ChoiceField(
        required=False,
        choices=[(None, "N/A"), ("Needed", "Needed"), ("Comleted", "Comleted")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Speedy Inventory",
    )
    labels_for_speedy_inventory = forms.ChoiceField(
        required=False,
        choices=[(None, "N/A"),("Needed", "Needed"), ("Comleted", "Comleted")],
        widget=forms.Select(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
        }),
        label="Labels for Speedy Inventory",
    )
    notes_dispatcher = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "border border-gray-300 rounded-md px-2 py-2 focus:outline-none focus:ring-2 focus:ring-red-500 w-full",
            "rows": 3,
            "placeholder": "Enter dispatch notes...",
        }),
        label="Dispatch Notes",
    )

    class Meta:
        model = Dispatch
        fields = [
            "ipad", "crew_leads", "drivers", "truck_1", "trailer_1", "truck_2", "trailer_2",
            "truck_3", "trailer_3", "truck_4", "trailer_4", "material", "special_equipment_needed",
            "special_equipment_status", "speedy_inventory_account", "speedy_inventory", 
            "labels_for_speedy_inventory", "notes_dispatcher",
        ]

    def __init__(self, *args, **kwargs):
        
        check= kwargs.pop('completed_order_id', None)

        # Get vehicles of type truck or trailer
        vehicles = Vehicle.objects.filter(vehicle_type__in=['truck', 'trailer'])

        # Get the latest availability data for each vehicle
        latest_dates = AvailabilityData.objects.filter(
            vehicle__in=vehicles
        ).values('vehicle').annotate(latest_date=Max('date_saved'))

        # Subquery to filter the latest record per vehicle with 'In Service' status
        latest_availability_data = AvailabilityData.objects.filter(
            vehicle__in=vehicles,
            date_saved__in=Subquery(latest_dates.values('latest_date')),
            status='In Service'
        )

        # Prefetch the latest availability data only for vehicles with 'In Service' availability
        vehicles_with_availability = vehicles.prefetch_related(
            Prefetch('availabilities', queryset=latest_availability_data, to_attr='availability')
        )

        # Separate trucks and trailers, filtering only those with 'In Service' availability data
        trucks = vehicles_with_availability.filter(vehicle_type='truck')
        trailers = vehicles_with_availability.filter(vehicle_type='trailer')

        if  check:
            truck_choices = [(truck.id, truck.name) for truck in trucks]
            trailer_choices = [(trailer.id, trailer.name) for trailer in trailers]

        else:
            truck_choices = [(None, "None")] + [(truck.id, truck.name) for truck in trucks if truck.availability]
            trailer_choices = [(None, "None")] + [(trailer.id, trailer.name) for trailer in trailers if trailer.availability]


        super().__init__(*args, **kwargs)

        # Dynamically set choices for truck and trailer fields
        for i in range(1, 5):
            self.fields[f'truck_{i}'].choices = truck_choices
            self.fields[f'trailer_{i}'].choices = trailer_choices

    
        