from django.shortcuts import render
from django.shortcuts import render,get_object_or_404
from django.views import View
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Q,Count,Max,DateField,Value,F
from django.db.models.functions import Coalesce
from django.http import HttpResponseForbidden
from authentication.models import UserProfile
from inspection.forms import  OnsiteInspectionForm, TrailerInspectionForm, TruckInspectionForm
from inspection.models import  Onsite_inspection, Trailer_inspection, Truck_inspection
from vehicle.models import Vehicle



def inspection_view(request):    

    """Render the home page."""
    return render(request, "vehicle_inspection_base.html")



class onsite_inspection_view(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)


    def get(self, request):
        
        step = int(request.GET.get("step", 1))
        # Define steps and the fields associated with each step
        steps = {
            1: ["job_number", "customer_name", "customer_phone", "pickup_address", "delivery_address", "crew_leader","crew_members"],
            2: ["materials_check_rating", "vehicle_inventory_rating", "customer_communication_rating", "parking_arranged_rating"],
            3: ["customer_greeted_rating", "crew_introduction_rating", "initial_walkthrough_rating", "estimate_comparison_rating",
                "initial_walkthrough_rating","damage_inspection_rating","paperwork_signed_rating","valuables_secured_rating",
                "protection_setup_rating","photos_sent_rating","inventory_management_rating","furniture_disassembly_rating",
                "parts_management_rating","loading_quality_rating","padding_used_rating","load_secured_rating","final_walkthrough_rating",
                "customer_initials_rating","follow_instructions_rating","truck_prepared_rating","dispatch_complete_rating"],
            4: ["dispatch_unload_rating", "damage_inspection_rating", "protection_setup_rating", "placement_accuracy_rating",
                "pad_management_rating","furniture_reassembly_rating","customer_walkthrough_rating","vehicle_inspection_rating",
                "final_charges_rating","customer_review_rating","paperwork_rating","payment_collection_rating","video_testimonial_rating",
                "completion_notice_rating"],
            5: ["comments", "customer_feedback"],
        }

        initial_data = {}
        for s in range(1, step):
            initial_data.update(request.session.get(f"step_{s}_data", {}))

        valid_keys = [field.name for field in Onsite_inspection._meta.fields] 
        initial_data = {key: value for key, value in initial_data.items() if key in valid_keys}

        if 'crew_leader' in initial_data:
            crew_leader_id = initial_data['crew_leader']
            try:
                crew_leader_instance = UserProfile.objects.get(id=crew_leader_id)
                initial_data['crew_leader'] = crew_leader_instance
            except UserProfile.DoesNotExist:
                initial_data['crew_leader'] = None

        if 'crew_members' in initial_data:
            crew_leader_id = initial_data['crew_members']
            try:
                crew_leader_instance = UserProfile.objects.get(id=crew_leader_id)
                initial_data['crew_members'] = crew_leader_instance
            except UserProfile.DoesNotExist:
                initial_data['crew_members'] = None

        inspection_instance = Onsite_inspection(**initial_data)
        prior_move_score = inspection_instance.calculate_prior_move_score()
        pickup_score = inspection_instance.calculate_pickup_score()
        dropoff_score = inspection_instance.calculate_dropoff_score()
        overall_score = inspection_instance.calculate_overall_score()

        crew_leader_choices = UserProfile.objects.all()  

        form = OnsiteInspectionForm(initial=initial_data)
        

        return render(request, "onsite_inspection.html", {
            "form": form, 
            "step": step, 
            "steps": steps, 
            "current_fields": steps[step],
            "crew_leader_choices": crew_leader_choices,  
            "prior_move_score":prior_move_score,
            "pickup_score":pickup_score,
            "dropoff_score":dropoff_score,
            "overall_score":overall_score,
        })

    def post(self, request):
        step = int(request.GET.get("step", 1))

        # Define steps and the fields associated with each step
        steps = {
            1: ["job_number", "customer_name", "customer_phone", "pickup_address", "delivery_address", "crew_leader", "crew_members"],
            2: ["materials_check_rating", "vehicle_inventory_rating", "customer_communication_rating", "parking_arranged_rating"],
            3: ["customer_greeted_rating", "crew_introduction_rating", "initial_walkthrough_rating", "estimate_comparison_rating",
                "initial_walkthrough_rating", "damage_inspection_rating", "paperwork_signed_rating", "valuables_secured_rating",
                "protection_setup_rating", "photos_sent_rating", "inventory_management_rating", "furniture_disassembly_rating",
                "parts_management_rating", "loading_quality_rating", "padding_used_rating", "load_secured_rating", "final_walkthrough_rating",
                "customer_initials_rating", "follow_instructions_rating", "truck_prepared_rating", "dispatch_complete_rating"],
            4: ["dispatch_unload_rating", "damage_inspection_rating", "protection_setup_rating", "placement_accuracy_rating",
                "pad_management_rating", "furniture_reassembly_rating", "customer_walkthrough_rating", "vehicle_inspection_rating",
                "final_charges_rating", "customer_review_rating", "paperwork_rating", "payment_collection_rating", "video_testimonial_rating",
                "completion_notice_rating"],
            5: ["comments", "customer_feedback"],
        }

        # Save the current step's data in the session
        crew_members = request.POST.getlist('crew_members')  
        if crew_members: 
            request.session[f"step_{step}_data"] = request.POST.copy() 
            request.session[f"step_{step}_data"]['crew_members'] = crew_members 
        else:
            request.session[f"step_{step}_data"] = request.POST

        # If it's the final step
        if step == len(steps):
            combined_data = {}

            # Collect data from all previous steps
            for s in range(1, len(steps) + 1):
                step_data = request.session.get(f"step_{s}_data", {})

                crew_members = step_data.get('crew_members', None)
                if crew_members:
                    if isinstance(crew_members, str): 
                        crew_members = crew_members.split(',')
                    if isinstance(crew_members, list):
                        if 'crew_members' in combined_data:
                            combined_data['crew_members'].extend(crew_members)  
                        else:
                            combined_data['crew_members'] = crew_members  

                combined_data.update(step_data)  

            combined_data["inspector"] = request.user.id  

            final_form = OnsiteInspectionForm(combined_data)

            if final_form.is_valid():
                final_instance = final_form.save(commit=False)
                final_instance.save()

                # Clear the session data after saving
                for s in range(1, len(steps) + 1):
                    request.session.pop(f"step_{s}_data", None)

                return redirect('onsite_inspection')

            return render(request, "onsite_inspection.html", {
                "form": final_form,
                "step": step,
                "steps": steps,
                "current_fields": steps[step],
            })
        else:
            return redirect(f"/station/onsite-inspection/?step={step + 1}")



class inspection_report_view(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Retrieve trucks and trailers from the Vehicle model
        trucks = Vehicle.objects.filter(vehicle_type='truck')
        trailers = Vehicle.objects.filter(vehicle_type='trailer')

        # Default to today's date for start and end dates
        start_date = request.GET.get('start_date', timezone.now().date())
        end_date = request.GET.get('end_date', timezone.now().date())

        # Parse the start and end dates if provided
        try:
            start_date = timezone.datetime.strptime(str(start_date), '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(str(end_date), '%Y-%m-%d').date()
        except ValueError:
            start_date = end_date = timezone.now().date()

        # Get the selected truck and trailer (if any)
        truck = request.GET.get('truck', None)
        trailer = request.GET.get('trailer', None)
        report_type = request.GET.get('report', '')

        # Initialize context
        context = {
            "start_date": start_date,
            "end_date": end_date,
            "truck": truck,
            "trailer": trailer,
            "report": report_type,
            "trucks": trucks,
            "trailers": trailers,
        }
        context["truck_inspections"] = Truck_inspection
        context["vehicle"] = 'Truck' if truck else 'Trailer'

        # Handling for different report types
        if report_type == "frequency":
            inspections = self._generate_frequency_report(start_date, end_date, truck, trailer)
            context["inspections"] = inspections

        elif report_type == "equipment":
            equipment_report, equipment_count = self._generate_equipment_report(start_date, end_date, truck, trailer)
            context["equipment_report"] = equipment_report
            context["equipment_count"] = equipment_count

        elif report_type == "comparison":
            comparison_report = self._generate_comparison_report(start_date, end_date, truck, trailer)
            context["comparison_report"] = comparison_report

        elif report_type == "readiness":
            readiness_report, readiness_count = self._generate_readiness_report(start_date, end_date, truck, trailer)
            context["readiness_report"] = readiness_report
            context["readiness_count"] = readiness_count

        elif report_type == "activity":
            activity_report = self._generate_activity_report(start_date, end_date,truck, trailer)
    
            # Send the data to the context to be used in the template
            context["activity_report"] = activity_report
            context["activity_count"] = len(activity_report)  # Number of drivers (length of the report)

        # Render the template with context
        return render(request, "inspection_report.html", context)

    def _generate_frequency_report(self, start_date, end_date, truck, trailer):
        inspections = []

        # Handle truck inspections
        if truck:
            truck_instance = get_object_or_404(Vehicle, id=truck)
            truck_inspections = Truck_inspection.objects.filter(
                truck=truck_instance, date__range=(start_date, end_date)
            )
            inspections.append(self._generate_inspection_report(truck_instance, truck_inspections))

        # Handle trailer inspections
        if trailer:
            trailer_instance = get_object_or_404(Vehicle, id=trailer)
            trailer_inspections = Trailer_inspection.objects.filter(
                trailer=trailer_instance, date__range=(start_date, end_date)
            )
            inspections.append(self._generate_inspection_report(trailer_instance,trailer_inspections))

        # Handle case when no specific vehicle is selected
        if not truck and not trailer:
            inspections.extend(self._generate_inspection_report_all_vehicles(start_date, end_date))

        return inspections

    def _generate_equipment_report(self, start_date, end_date, truck, trailer):
        # List of fields that use GENERAL_CHOICES and could have the value "missing-not restocked"
        fields_to_check_truck = [
            'first_aid_kit',
            'floor_mats',
            'business_cards',
            'business_cards_magnetic',
            'fuses',
            'two_pens',
            'sharpie',
            'camera',
            'flash_light',
            'sun_visor',
            'geo_tab',
            'jack_and_links',
            'cab_card',
            'registration',
            'insurance_card',
            'accident_report_form',
            'process_of_accident',
            'fire_extinguisher',
            'four_way',
            'min_7_orange',
            'hazard_triangle_x3',
            'jumper_cables',
            'large_door_stops',
            'trash_bag',
            'roll_paper_towels',
            'small_hand',
            'bottle_jack',
            'cones',
            'spare_tire',
            'condition_spare_tyre'
        ]

        fields_to_check_trailer = [
            'trash',  # Trash field
            'blanket_84',
            'hand_trucks_with_covers',
            'four_wheel_dolly',
            'short_straps',
            'long_straps',
            'ramp',
            'rubber_bands',
            'red_floor_runner',
            'forearm_straps',
            'wardrobe_boxes_with_bars',
            'tv_box_for_rental',
            'multi_tool_set',
            'hand_tools_bag',
            'two_carabiner',
            'broom'
        ]

        # Construct the Q object to check for 'missing-not restocked' in any of the fields
        queries_truck = Q()
        for field in fields_to_check_truck:
            queries_truck |= Q(**{f'{field}__exact': 'missing-not restocked'})

        queries_trailer = Q()
        for field in fields_to_check_trailer:
            queries_trailer |= Q(**{f'{field}__exact': 'missing-not restocked'})

        if truck :
            # Now apply the date range filter and the missing equipment filter
            missing_equipment_trucks = Truck_inspection.objects.filter(
                queries_truck, 
                truck=truck,
                date__range=(start_date, end_date)
            )
        else:
            missing_equipment_trucks = Truck_inspection.objects.filter(
                queries_truck, 
                date__range=(start_date, end_date)
            )
        
        if trailer:
            missing_equipment_trailers = Trailer_inspection.objects.filter(
                queries_trailer, 
                trailer=trailer,
                date__range=(start_date, end_date)
            )
        else:
            missing_equipment_trailers = Trailer_inspection.objects.filter(
                queries_trailer, 
                date__range=(start_date, end_date)
            )


        equipment_report = []

        # Collect truck equipment that is missing/not restocked
        for inspection in missing_equipment_trucks:
            truck_instance = inspection.truck
            missing_items = []
            
            for field in fields_to_check_truck:
                if getattr(inspection, field) == "missing-not restocked":
                    missing_items.append({
                        "item": field.replace("_", " ").capitalize(),  # Clean up field name for display
                        "inspection_date": inspection.date
                    })
            
            if missing_items:
                equipment_report.append({
                    "vehicle": truck_instance,
                    "missing_items": missing_items
                })

        # Collect trailer equipment that is missing/not restocked
        for inspection in missing_equipment_trailers:
            trailer_instance = inspection.trailer
            missing_items = []
            
            for field in fields_to_check_trailer:
                if getattr(inspection, field) == "missing-not restocked":
                    missing_items.append({
                        "item": field.replace("_", " ").capitalize(),  # Clean up field name for display
                        "inspection_date": inspection.date
                    })

            if missing_items:
                equipment_report.append({
                    "vehicle": trailer_instance,
                    "missing_items": missing_items
                })

        return equipment_report, len(equipment_report)

    def _generate_comparison_report(self, start_date, end_date, truck, trailer):
        # If no truck is provided, we want to get all trucks
        if truck:
            truck_instance = get_object_or_404(Vehicle, id=truck)
            truck_filter = {'truck': truck_instance}
        else:
            truck_filter = {}  # No truck filter, so we want all trucks

        # If no trailer is provided, we want to get all trailers
        if trailer:
            trailer_instance = get_object_or_404(Vehicle, id=trailer)
            trailer_filter = {'trailer': trailer_instance}
        else:
            trailer_filter = {}  # No trailer filter, so we want all trailers

        inspection_comparison_report = []

        # Query truck and trailer inspections for driver and manager with the respective filters
        driver_truck_inspections = Truck_inspection.objects.filter(
            **truck_filter,
            saved_by__role='driver',
            date__range=(start_date, end_date)
        )

        driver_trailer_inspections = Trailer_inspection.objects.filter(
            **trailer_filter,
            saved_by__role='driver',
            date__range=(start_date, end_date)
        )

        manager_truck_inspections = Truck_inspection.objects.filter(
            **truck_filter,
            saved_by__role='manager',
            date__range=(start_date, end_date)
        )

        manager_trailer_inspections = Trailer_inspection.objects.filter(
            **trailer_filter,
            saved_by__role='manager',
            date__range=(start_date, end_date)
        )

        # Combine truck and trailer inspections for driver and manager
        driver_inspections_data = list(driver_truck_inspections) + list(driver_trailer_inspections)
        manager_inspections_data = list(manager_truck_inspections) + list(manager_trailer_inspections)

        # Iterate over manager inspections and compare with driver inspections
        for manager_inspection in manager_inspections_data:
            discrepancies = []

            # Find the corresponding driver inspection based on vehicle and date
            driver_inspection = None
            if isinstance(manager_inspection, Truck_inspection):
                driver_inspection = next(
                    (d for d in driver_inspections_data 
                    if isinstance(d, Truck_inspection) and d.truck.id == manager_inspection.truck.id and d.date == manager_inspection.date),
                    None
                )
            elif isinstance(manager_inspection, Trailer_inspection):
                driver_inspection = next(
                    (d for d in driver_inspections_data 
                    if isinstance(d, Trailer_inspection) and d.trailer.id == manager_inspection.trailer.id and d.date == manager_inspection.date),
                    None
                )

            # If there's no corresponding driver inspection, add a discrepancy
            if not driver_inspection:
                discrepancies.append(f"No driver inspection found for {manager_inspection.truck if isinstance(manager_inspection, Truck_inspection) else manager_inspection.trailer} on {manager_inspection.date}")
            else:
                # Compare all fields between the manager and driver inspections
                manager_fields = vars(manager_inspection)
                driver_fields = vars(driver_inspection)

                # Loop through each field in manager inspection and compare with driver inspection
                for field, manager_value in manager_fields.items():
                    if field not in ['id', 'date', 'saved_by', 'date_saved']:  # Exclude fields that shouldn't be compared
                        driver_value = driver_fields.get(field)

                        # Check for discrepancy
                        if manager_value != driver_value:
                            # Create a readable description of the discrepancy
                            discrepancies.append(f"Discrepancy in {field}: {manager_value} vs {driver_value}")

            # If there's no corresponding manager inspection, add a discrepancy
            if not manager_inspection:
                discrepancies.append(f"No manager inspection found for {driver_inspection.truck if isinstance(driver_inspection, Truck_inspection) else driver_inspection.trailer} on {driver_inspection.date}")
            
            # If discrepancies exist, add them to the report
            if discrepancies:
                inspection_comparison_report.append({
                    'vehicle': manager_inspection.truck if isinstance(manager_inspection, Truck_inspection) else manager_inspection.trailer,
                    'driver': driver_inspection.saved_by.user.username if driver_inspection else 'N/A',
                    'manager': manager_inspection.saved_by.user.username,
                    'inspection_date': manager_inspection.date,
                    'discrepancies': discrepancies
                })

        return inspection_comparison_report

    def _generate_readiness_report(self, start_date, end_date, truck, trailer):
        readiness_report = []

        # Generate report for specific truck if provided
        if truck:
            truck_instance = get_object_or_404(Vehicle, id=truck)
            truck_readiness = Truck_inspection.objects.filter(
                truck=truck_instance,
                date__range=(start_date, end_date)
            ).order_by('-date')[:1] 
            readiness_report.append(self._generate_readiness_report_data(truck_instance, truck_readiness))

        # Generate report for specific trailer if provided
        if trailer:
            trailer_instance = get_object_or_404(Vehicle, id=trailer)
            trailer_readiness = Trailer_inspection.objects.filter(
                trailer=trailer_instance,
                date__range=(start_date, end_date)
            )
            readiness_report.append(self._generate_readiness_report_data(trailer_instance, trailer_readiness))

        # Generate report for all vehicles (truck and trailer)
        if not truck and not trailer:
            readiness_report = []

            # Get all unique trucks
            all_trucks = Vehicle.objects.filter(vehicle_type='truck')  # Assuming 'vehicle_type' is used to identify trucks
            for truck_instance in all_trucks:
                # Get inspections for this truck in the date range
                truck_related_inspections = Truck_inspection.objects.filter(
                    truck=truck_instance, date__range=(start_date, end_date)
                ).order_by('-date')[:1] 

                if truck_related_inspections.exists():
                    # If there are inspections, generate the report
                    readiness_report.append(self._generate_readiness_report_data(truck_instance, truck_related_inspections))
                else:
                    # If no inspections, add the vehicle with None or null for inspection data
                    readiness_report.append(self._generate_readiness_report_data(truck_instance, []))  # Passing empty list if no inspections

            # Get all unique trailers
            all_trailers = Vehicle.objects.filter(vehicle_type='trailer')  # Assuming 'vehicle_type' is used to identify trailers
            for trailer_instance in all_trailers:
                # Get inspections for this trailer in the date range
                trailer_related_inspections = Trailer_inspection.objects.filter(
                    trailer=trailer_instance, date__range=(start_date, end_date)
                ).order_by('-date')[:1] 

                if trailer_related_inspections.exists():
                    # If there are inspections, generate the report
                    readiness_report.append(self._generate_readiness_report_data(trailer_instance, trailer_related_inspections))
                else:
                    # If no inspections, add the vehicle with None or null for inspection data
                    readiness_report.append(self._generate_readiness_report_data(trailer_instance, []))  # Passing empty list if no inspections


        return readiness_report, len(readiness_report)

    def _generate_activity_report(self, start_date, end_date, truck, trailer):
        # Initialize filters for truck and trailer inspections
        truck_filter = Q()
        trailer_filter = Q()

        # If truck is provided, filter inspections for the specific truck
        if truck:
            truck_instance = get_object_or_404(Vehicle, id=truck)
            truck_filter = Q(truck_inspection__truck=truck_instance)

        # If trailer is provided, filter inspections for the specific trailer
        if trailer:
            trailer_instance = get_object_or_404(Vehicle, id=trailer)
            trailer_filter = Q(trailer_inspection__trailer=trailer_instance)

        # Get users with 'driver' or 'manager' roles
        users = UserProfile.objects.filter(role__in=['manager', 'driver'])

        # Annotate with inspection counts and last inspection date for each user
        driver_inspections_count = (
            users
            .annotate(
                # Count inspections for truck within the date range, considering filters
                truck_inspections_count=Count(
                    'truck_inspection',
                    distinct=True,
                    filter=Q(truck_inspection__date__range=(start_date, end_date)) & truck_filter
                ),

                # Count inspections for trailer within the date range, considering filters
                trailer_inspections_count=Count(
                    'trailer_inspection',
                    distinct=True,
                    filter=Q(trailer_inspection__date__range=(start_date, end_date)) & trailer_filter
                ),

                # Total count of inspections (truck + trailer inspections)
                inspections_count=F('truck_inspections_count') + F('trailer_inspections_count'),

                # Get the last inspection date for Truck and Trailer separately, applying the filters
                last_truck_inspection_date=Max(
                    'truck_inspection__date', 
                    filter=Q(truck_inspection__date__range=(start_date, end_date)) & truck_filter
                ),
                last_trailer_inspection_date=Max(
                    'trailer_inspection__date', 
                    filter=Q(trailer_inspection__date__range=(start_date, end_date)) & trailer_filter
                )
            )
            .annotate(
                # Combine the last inspection dates (from either Truck or Trailer)
                last_inspection_date=Coalesce(
                    'last_truck_inspection_date', 
                    'last_trailer_inspection_date',
                    Value('1900-01-01', output_field=DateField())  # Default to '1900-01-01' if no inspections
                )
            )
            .values('id', 'user__username', 'role', 'inspections_count', 'last_inspection_date')  # Include username, role, inspections count, and last inspection date
        )

        return driver_inspections_count

    def _generate_inspection_report(self, vehicle_instance, inspections):
        # Check if inspections is empty
        if not inspections:
            return {
                "vehicle": vehicle_instance,
                "inspection_count": 0,
                "last_inspection": None,
                "inspection_difference": None,
            }

        # If there are inspections, get the most recent inspection
        last_inspection = inspections.order_by('-date').first()  # Get the most recent inspection
        return {
            "vehicle": vehicle_instance,
            "inspection_count": inspections.count(),
            "last_inspection": last_inspection.date if last_inspection else None,
            "inspection_difference": (timezone.now().date() - last_inspection.date).days if last_inspection else None,
        }

    def _generate_comparison_report_data(self, vehicle_instance, vehicle_type, driver_inspections, manager_inspections):
        last_driver_inspection = driver_inspections.order_by('-date').first()
        last_manager_inspection = manager_inspections.order_by('-date').first()

        return {
            "vehicle_name": vehicle_instance.name,
            "vehicle_type": vehicle_type,
            "driver_inspection_count": driver_inspections.count(),
            "manager_inspection_count": manager_inspections.count(),
            "last_driver_inspection": last_driver_inspection.date if last_driver_inspection else None,
            "last_manager_inspection": last_manager_inspection.date if last_manager_inspection else None,
            "driver_inspection_difference": (timezone.now().date() - last_driver_inspection.date).days if last_driver_inspection else None,
            "manager_inspection_difference": (timezone.now().date() - last_manager_inspection.date).days if last_manager_inspection else None,
        }

    def _generate_readiness_report_data(self, vehicle_instance, inspections):
        ready_values = ['present']
        ready_count = 0
        total_count = 0

        # Define the fields to check for readiness status
        if vehicle_instance.vehicle_type == "truck":
            inspection_fields = [
                'first_aid_kit', 'floor_mats', 'business_cards', 'business_cards_magnetic',
                'fuses', 'two_pens', 'sharpie', 'camera', 'flash_light', 'sun_visor',
                'geo_tab', 'jack_and_links', 'cab_card', 'registration', 'insurance_card',
                'accident_report_form', 'process_of_accident', 'fire_extinguisher', 'four_way',
                'min_7_orange', 'hazard_triangle_x3', 'jumper_cables', 'large_door_stops', 
                'trash_bag', 'roll_paper_towels', 'small_hand', 'bottle_jack', 'cones', 'spare_tire'
            ]
        elif vehicle_instance.vehicle_type == "trailer":
            inspection_fields = [
                'trash', 'blanket_84', 'hand_trucks_with_covers', 'four_wheel_dolly', 'short_straps',
                'long_straps', 'ramp', 'rubber_bands', 'red_floor_runner', 'forearm_straps',
                'wardrobe_boxes_with_bars', 'tv_box_for_rental', 'multi_tool_set', 'hand_tools_bag',
                'two_carabiner', 'broom'
            ]
        else:
            inspection_fields = []

        # If inspections is a queryset with multiple records or an empty list (no inspections)
        ready_count = 0
        total_count = 0
        overall_ready_count = 0
        overall_total_count = 0
        overall_readiness_score = 0

        if inspections:  # If inspections exist (either empty list or actual data)
            for inspection in inspections:
                ready_count = 0
                total_count = 0

                # Count ready items and total items
                for field in inspection_fields:
                    value = getattr(inspection, field)
                    if value in ready_values:
                        ready_count += 1
                    if value is not None:  # Increment total count if the value is not None
                        total_count += 1

                # Calculate readiness score as a percentage of ready items
                readiness_score = (ready_count / len(inspection_fields)) * 100 if total_count else 0

                # Aggregate readiness score and counts for all vehicles
                overall_ready_count += ready_count
                overall_total_count += len(inspection_fields)  # Using len(inspection_fields) for total items
                overall_readiness_score += readiness_score

            # Calculate overall readiness score for all inspections
            if overall_total_count > 0:
                overall_readiness_score = (overall_ready_count / overall_total_count) * 100
            else:
                overall_readiness_score = 0

            # Return a report that combines all vehicles
            report_data = {
                'vehicle': vehicle_instance,
                'last_inspection': inspections[0].date if inspections else None,  # Get last inspection date
                'readiness_score': round(overall_readiness_score, 2),
                'ready_items': overall_ready_count,
                'total_items': overall_total_count
            }

        else:
            # If no inspections exist, just return the vehicle with a default readiness score of 0
            report_data = {
                'vehicle': vehicle_instance,
                'last_inspection': None,
                'readiness_score': 0.0,
                'ready_items': 0,
                'total_items': len(inspection_fields)  # All items in the field list are considered total
            }

        return report_data

    def _generate_inspection_report_all_vehicles(self, start_date, end_date):
        """ Helper method to generate report data for all vehicles in the specified date range. """
        inspections = []

        # Get all unique trucks
        all_trucks = Vehicle.objects.filter(vehicle_type='truck')  # Assuming 'is_truck' identifies trucks
        for truck in all_trucks:
            # Get inspections for this truck in the date range
            truck_related_inspections = Truck_inspection.objects.filter(
                truck=truck, date__range=(start_date, end_date)
            )
            
            if truck_related_inspections.exists():
                # If there are inspections, generate the report
                inspections.append(self._generate_inspection_report(truck, truck_related_inspections))
            else:
                # If no inspections, add the vehicle with None or null for inspection data
                inspections.append(self._generate_inspection_report(truck, []))  # Passing empty list if no inspections

        # Get all unique trailers
        all_trailers = Vehicle.objects.filter(vehicle_type='trailer')  # Assuming 'is_truck=False' identifies trailers
        for trailer in all_trailers:
            # Get inspections for this trailer in the date range
            trailer_related_inspections = Trailer_inspection.objects.filter(
                trailer=trailer, date__range=(start_date, end_date)
            )
            
            if trailer_related_inspections.exists():
                # If there are inspections, generate the report
                inspections.append(self._generate_inspection_report(trailer, trailer_related_inspections))
            else:
                # If no inspections, add the vehicle with None or null for inspection data
                inspections.append(self._generate_inspection_report(trailer, []))  # Passing empty list if no inspections

        return inspections

    def _generate_activity_report_data(self, inspections, role):
        report_data = []
        inspectors = inspections.values("inspector").distinct()

        for inspector in inspectors:
            inspector_inspections = inspections.filter(inspector=inspector["inspector"])
            last_inspection = inspector_inspections.order_by('-date').first()
            report_data.append({
                "inspector": inspector_inspections.first().inspector.name,
                "role": role,
                "inspection_count": inspector_inspections.count(),
                "last_inspection": last_inspection.date if last_inspection else None,
                "inspection_difference": (timezone.now().date() - last_inspection.date).days if last_inspection else None,
            })

        return report_data



class trailer_inspection_view(View):   

    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs) 

    def get(self,request):
        form = TrailerInspectionForm()
        excluded_fields = ['date', 'trailer', 'clean_status', 'trash']
        return render(request, "trailer_inspection.html",{"form":form,"excluded_fields":excluded_fields})
    
    def post(self, request):

        form = TrailerInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            current_user=request.user
            user=UserProfile.objects.get(user=current_user)
            inspection.saved_by=user
            
            inspection.save()

            return redirect('trailer_inspection')
        
        return render(request, "trailer_inspection.html", {"form": form})



class truck_inspection_view(View):   

    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs) 

    def get(self,request):
        form = TruckInspectionForm()
        excluded_fields=['date', 'truck', 'clean_status', 'in_cab', 'bed_of_truck','cones','spare_tire','condition_spare_tyre']
        in_cab_field=['first_aid_kit','floor_mats','business_cards','business_cards_magnetic','fuses','two_pens',
                      'sharpie','camera','flash_light','sun_visor','geo_tab','jack_and_links','cab_card','registration',
                      'insurance_card','accident_report_form','process_of_accident']
        return render(request, "truck_inspection.html",{"form":form,"excluded_fields":excluded_fields,"in_cab_field":in_cab_field})
    
    def post(self, request):
        form = TruckInspectionForm(request.POST)
        if form.is_valid():
            inspection = form.save(commit=False)
            current_user=request.user
            user=UserProfile.objects.get(user=current_user)
            inspection.saved_by=user
            inspection.save()

            return redirect('truck_inspection')
        
        return render(request, "truck_inspection.html", {"form": form})
