import json

from inventory_app.permissions import IsManager
from .models import AvailabilityData, Dispatch, Order, Vehicle
from .forms import  DispatchForm, OrderForm
from django.shortcuts import render, get_object_or_404
from django.views import View
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Prefetch
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.db.models import Q
from django.db.models import Max, Subquery, Prefetch, Q
from datetime import timedelta
from django.http import HttpResponseForbidden



def availability_logistic_view(request):

    """Render the home page."""
    return render(request, "availability_logistic_base.html")


class vehicle_availability_view(View):

    permission_classes = [IsAuthenticated, IsManager] 
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Default to today if no date is provided
        selected_date_str = request.GET.get('date', timezone.now().date())

        # Parse the date string into a date object
        if isinstance(selected_date_str, str):
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = selected_date_str

        # Get all vehicles of type 'truck' or 'trailer'
        vehicles = Vehicle.objects.filter(vehicle_type__in=['truck', 'trailer'])

        # Get the latest availability data for the selected date for each vehicle
        latest_availability_data = AvailabilityData.objects.filter(
            vehicle__in=vehicles
        ).annotate(date_only=TruncDate('date_saved'))  # Truncate the time component of `date_saved`

        # Filter the availability data for the selected date
        latest_availability_data = latest_availability_data.filter(date_only=selected_date)

        # For each vehicle, fetch the latest availability data (order by `date_saved` descending)
        latest_availability_data = latest_availability_data.order_by('-date_saved')

        # Now we can annotate the vehicles with their latest availability data
        vehicles_with_availability = vehicles.prefetch_related(
            Prefetch(
                'availabilities',
                queryset=latest_availability_data,
                to_attr='availability'  # This will attach the results to the `availability` attribute
            )
        )

        # Separate trucks and trailers
        trucks = vehicles_with_availability.filter(vehicle_type='truck')
        trailers = vehicles_with_availability.filter(vehicle_type='trailer')

        # Render the result to the template
        return render(request, "truck_availability.html", {
            "trucks": trucks,
            "trailers": trailers,
            "selected_date": selected_date,
        })

    
    def post(self, request):
        # Extract the selected date (default to today if empty)
        selected_date_str = request.POST.get('date')
        if selected_date_str:
            selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
        else:
            selected_date = timezone.now().date()

        # Process updates for truck and trailer availability
        for key in request.POST:
            # Process both status and estimated date fields
            if key.startswith('truck_') or key.startswith('trailer_'):
                # Ensure the key has the correct format
                parts = key.split('_')
                if len(parts) < 2:
                    continue  # Skip invalid keys

                try:
                    vehicle_id = int(parts[1])  # Extract vehicle ID
                except ValueError:
                    continue  # Skip if the vehicle_id is not a valid integer

                vehicle = get_object_or_404(Vehicle, id=vehicle_id)

                if key.endswith('_date'):  # Handle estimated return date
                    estimated_return_date = request.POST.get(key)
                    if estimated_return_date:
                        estimated_return_date = timezone.datetime.strptime(estimated_return_date, '%Y-%m-%d').date()
                    else:
                        estimated_return_date = None

                    # Fetch the latest availability data for the vehicle
                    current_availability = AvailabilityData.objects.filter(vehicle=vehicle).last()

                    # Update estimated_back_in_service_date only if it has changed
                    if current_availability and current_availability.estimated_back_in_service_date != estimated_return_date:
                        new_availability = AvailabilityData(
                            vehicle=vehicle,
                            status=current_availability.status,
                            date_saved=selected_date,
                            estimated_back_in_service_date=estimated_return_date,
                        )
                        new_availability.save()

                else:  # Handle status
                    status = request.POST.get(key)  # Extract the status value directly

                    # Fetch the latest availability data for the vehicle
                    current_availability = AvailabilityData.objects.filter(vehicle=vehicle).last()

                    # Create a new record only if the status has changed
                    if not current_availability or current_availability.status != status:

                        # Create a new record
                        new_availability = AvailabilityData(
                            vehicle=vehicle,
                            status=status,
                            date_saved=selected_date,
                            back_in_service_date=selected_date if status == "In Service" else None,
                            estimated_back_in_service_date=current_availability.estimated_back_in_service_date if current_availability else None
                        )
                        new_availability.save()

        # Redirect back to the same page with the selected date to reflect updated data
        return redirect(f'/vehicle-availability/?date={selected_date}')

       
class JobLogisticsPage(View):

    permission_classes = [IsAuthenticated, IsManager] 
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form1 = OrderForm()
        form2 = DispatchForm()
        job_orders = Order.objects.filter(status='Pending') 
        dispatch = Dispatch.objects.filter(status='Completed') 
        return render(request, "job_logistics.html", {"form":form1,"form2":form2, "job_orders": job_orders,"dispatches": dispatch})
    
    def post(self, request):
        job_orders = Order.objects.filter(status="Pending")  # Fetch pending orders
        dispatches = Dispatch.objects.filter(status='Completed')  # Fetch all dispatches
        completed_order_id = request.POST.get('completed_order_id')
        
        if completed_order_id:
            # Pass the selected completed order ID to the form
            form2 = DispatchForm(request.POST or None, completed_order_id=completed_order_id)

        # Initialize both forms without data
        form1 = OrderForm()
        # form2 = DispatchForm()
        if completed_order_id:
            # Pass the selected completed order ID to the form
            form2 = DispatchForm(request.POST or None, completed_order_id=completed_order_id)
        else:
            form2 = DispatchForm()


        # Handle OrderForm submission
        if 'submit_order' in request.POST:

            form1 = OrderForm(request.POST)
            if form1.is_valid():
                order = form1.save(commit=False)
                order.saved_by = request.user.username
                order.saved_on=timezone.now().date()
                order.save()
                return redirect('/job-logistics/')
            
        
        elif 'submit_dispatch' in request.POST:
            form2 = DispatchForm(request.POST)

            if form2.is_valid():
                selected_order_id = request.POST.get("selected_pending_order")
                if selected_order_id:
                    try:
                        # Fetch the selected pending order
                        order_obj = Order.objects.get(id=selected_order_id, status="Pending")
                        
                        # Assign the selected order to the Dispatch instance
                        form2.instance.order = order_obj
                        form2.instance.status = 'Completed'

                        # Update order status to Completed
                        order_obj.status = 'Completed'
                        order_obj.save()

                        # Save the Dispatch instance
                        dispatch = form2.save(commit=False)
                        dispatch.submitted_by = request.user.username
                        dispatch.submitted_on=timezone.now().date()
                        dispatch.save()

                        # Update AvailabilityData for selected trucks and trailers
                        truck_fields = ['truck_1', 'truck_2', 'truck_3', 'truck_4']
                        trailer_fields = ['trailer_1', 'trailer_2', 'trailer_3', 'trailer_4']

                        # Combine truck and trailer IDs into one list
                        selected_vehicle_ids = [
                            form2.cleaned_data.get(field)
                            for field in truck_fields + trailer_fields
                            if form2.cleaned_data.get(field)
                        ]
                        
                        for vehicle_id in selected_vehicle_ids:
                            # Fetch the latest AvailabilityData record for the vehicle
                            current_availability = AvailabilityData.objects.filter(vehicle__id=vehicle_id).order_by('-date_saved').first()
                            
                            if current_availability:
                                # Create a new AvailabilityData record for this vehicle
                                new_availability = AvailabilityData(
                                    vehicle_id=vehicle_id,
                                    status='Out of Service', 
                                    date_saved=timezone.now().date(),
                                )
                                new_availability.save()

                        return redirect('/job-logistics/')
                    except Order.DoesNotExist:
                        form2.add_error(None, "Selected order does not exist or is not pending.")
                else:
                    form2.add_error(None, "No order selected. Please select a pending order.")
            else:
                # Log errors for debugging
                print("Dispatch form errors:", form2.errors)

        # If neither form is valid or no form is submitted, render the page with both forms and their errors
        return render(request, "job_logistics.html", {
            "form": form1,
            "form2": form2,
            "job_orders": job_orders, 
            "dispatches": dispatches,
        })


class availability_report(View):

    permission_classes = [IsAuthenticated, IsManager] 
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Retrieve start and end dates from the GET request
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')


        # Default to today if no date is provided
        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = end_date = timezone.now().date()

        # Fetch all vehicles (trucks and trailers)
        vehicles = Vehicle.objects.filter(vehicle_type__in=['truck', 'trailer'])

        # Get the latest availability data for each vehicle within the date range
        latest_dates = AvailabilityData.objects.filter(
            vehicle__in=vehicles,
            date_saved__lte=end_date
        ).values('vehicle', 'date_saved').annotate(latest_date=Max('date_saved'))

        # Subquery to filter the latest record per vehicle per day
        latest_availability_data = AvailabilityData.objects.filter(
            vehicle__in=vehicles,
            date_saved__in=Subquery(latest_dates.values('latest_date'))
        )

        # Prefetch the latest availability data for each vehicle
        vehicles_with_availability = vehicles.prefetch_related(
            Prefetch('availabilities', queryset=latest_availability_data, to_attr='availability')
        )

        # Separate trucks and trailers
        trucks = vehicles_with_availability.filter(vehicle_type='truck')
        trailers = vehicles_with_availability.filter(vehicle_type='trailer')

        truck_data = []
        trailer_data = []

        def calculate_in_service_days(out_of_service_days_count, start_date, end_date):
            total_days = (end_date - start_date).days + 1
            in_service_days = total_days - out_of_service_days_count
            return in_service_days

        # Calculate In-Service and Out-of-Service days for Trucks
        for truck in trucks:
            # Get all availability data for the truck, ordered by date (descending)
            availability_data = sorted(truck.availability, key=lambda x: x.date_saved, reverse=True)

            out_of_service_days_count = 0
            for day in range((end_date - start_date).days + 1):
                current_day = start_date + timedelta(days=day)
                
                # Get the latest availability record for the current day
                day_records = [record for record in availability_data if record.date_saved.date() == current_day]

                if day_records:
                    latest_data = day_records[0]  # The latest record for that day

                    if latest_data.status == "Out of Service":
                        # Count out-of-service days for the current day
                        out_of_service_start = max(latest_data.date_saved.date(), start_date)
                        out_of_service_end = min(latest_data.back_in_service_date, end_date) if latest_data.back_in_service_date else end_date

                        if out_of_service_start <= out_of_service_end:
                            out_of_service_days_count += 1

            # Calculate in-service days
            in_service_days = calculate_in_service_days(out_of_service_days_count, start_date, end_date)

            truck_data.append({
                "name": truck.name,
                "in_service_days": in_service_days,
                "out_of_service_days": out_of_service_days_count
            })

        # Calculate In-Service and Out-of-Service days for Trailers
        for trailer in trailers:
            # Get all availability data for the trailer, ordered by date (descending)
            availability_data = sorted(trailer.availability, key=lambda x: x.date_saved, reverse=True)

            out_of_service_days_count = 0
            for day in range((end_date - start_date).days + 1):
                current_day = start_date + timedelta(days=day)
                
                # Get the latest availability record for the current day
                day_records = [record for record in availability_data if record.date_saved.date() == current_day]

                if day_records:
                    latest_data = day_records[0]  # The latest record for that day

                    if latest_data.status == "Out of Service":
                        # Count out-of-service days for the current day
                        out_of_service_start = max(latest_data.date_saved.date(), start_date)
                        out_of_service_end = min(latest_data.back_in_service_date, end_date) if latest_data.back_in_service_date else end_date

                        if out_of_service_start <= out_of_service_end:
                            out_of_service_days_count += 1

            # Calculate in-service days
            in_service_days = calculate_in_service_days(out_of_service_days_count, start_date, end_date)

            trailer_data.append({
                "name": trailer.name,
                "in_service_days": in_service_days,
                "out_of_service_days": out_of_service_days_count
            })

        # Total days in the range
        total_days = (end_date - start_date).days + 1

        # Return the data to the template
        return render(request, "availability_report.html", {
            "start_date": start_date,
            "end_date": end_date,
            "truck_data": truck_data,
            "trailer_data": trailer_data,
            "total_days": total_days,
        })


class logistic_report(View):

    permission_classes = [IsAuthenticated, IsManager] 
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        # Retrieve start and end dates from the GET request
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Default to today if no date is provided
        if start_date_str and end_date_str:
            start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = end_date = timezone.now().date()

        # Get the report type from the query string
        report_type = request.GET.get('report_type', 'daily_job_summary')

        # Query the necessary data based on the report type
        job_summary = []
        crew_performance = []
        vehicle_utilization = []
        referral_effectiveness = []

        if report_type == 'daily_job_summary':
            # Prefetch related dispatch data
            job_summary = Order.objects.filter(date__range=[start_date, end_date]).prefetch_related(
                'dispatches'  # Prefetch the related dispatches
            ).values(
                'date', 'job_no', 'last_name_customer', 'phone_number', 'type_of_move',
                'moved_before', 'moved_before_crew_name', 'referral_source', 'crew_name', 
                'crew_available', 'number_of_trucks', 'number_of_trailers', 'notes_order_detail', 
                'saved_by', 'saved_on', 'dispatches__ipad', 'dispatches__crew_leads', 
                'dispatches__drivers', 'dispatches__truck_1', 'dispatches__trailer_1', 
                'dispatches__truck_2', 'dispatches__trailer_2', 'dispatches__truck_3', 
                'dispatches__trailer_3', 'dispatches__truck_4', 'dispatches__trailer_4', 
                'dispatches__material', 'dispatches__special_equipment_needed', 
                'dispatches__special_equipment_status', 'dispatches__speedy_inventory_account', 
                'dispatches__speedy_inventory', 'dispatches__labels_for_speedy_inventory', 
                'dispatches__notes_dispatcher', 'dispatches__submitted_by', 'dispatches__submitted_on'
            )

        elif report_type == 'crew_performance':
            crew_performance = Dispatch.objects.filter(
                order__date__range=[start_date, end_date]  # Filter dispatches by order's date
            ).values('order__crew_name').annotate(total_dispatch_orders=Count('id')) 

        elif report_type == 'vehicle_utilization':
            vehicle_utilization = Dispatch.objects.filter(order__date__range=[start_date, end_date]).values(
                'truck_1', 'trailer_1', 'truck_2', 'trailer_2', 'truck_3', 'trailer_3', 'truck_4', 'trailer_4'
            ).annotate(
                truck_1_usage=Count('truck_1', filter=~Q(truck_1=None)),
                trailer_1_usage=Count('trailer_1', filter=~Q(trailer_1=None)),
                truck_2_usage=Count('truck_2', filter=~Q(truck_2=None)),
                trailer_2_usage=Count('trailer_2', filter=~Q(trailer_2=None)),
                truck_3_usage=Count('truck_3', filter=~Q(truck_3=None)),
                trailer_3_usage=Count('trailer_3', filter=~Q(trailer_3=None)),
                truck_4_usage=Count('truck_4', filter=~Q(truck_4=None)),
                trailer_4_usage=Count('trailer_4', filter=~Q(trailer_4=None))
            ).distinct()

            # Transform the data to include vehicle names if necessary
            vehicle_utilization = [{
                'vehicle': vehicle['truck_1'] or vehicle['trailer_1'] or vehicle['truck_2'] or vehicle['trailer_2'] or 
                        vehicle['truck_3'] or vehicle['trailer_3'] or vehicle['truck_4'] or vehicle['trailer_4'],
                'utilization': sum([
                    vehicle['truck_1_usage'],
                    vehicle['trailer_1_usage'],
                    vehicle['truck_2_usage'],
                    vehicle['trailer_2_usage'],
                    vehicle['truck_3_usage'],
                    vehicle['trailer_3_usage'],
                    vehicle['truck_4_usage'],
                    vehicle['trailer_4_usage']
                ])
            } for vehicle in vehicle_utilization]

        elif report_type == 'referral_effectiveness':
            referral_effectiveness = Order.objects.filter(date__range=[start_date, end_date]).values('referral_source').annotate(job_count=Count('referral_source'))

        # Total days in the range
        total_days = (end_date - start_date).days + 1

        return render(request, "logistic_report.html", {
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "job_summary": job_summary,
            "crew_performance": crew_performance,
            "vehicle_utilization": vehicle_utilization,
            "referral_effectiveness": referral_effectiveness,
            "report_type": report_type,
        })