from django.shortcuts import render
from django.views import View
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect
from django.utils import timezone
from django.db.models import Q
from django.db.models import Q
from django.http import HttpResponseForbidden
from station.forms import FleetOrderForm, StationInspectionForm, VehicleInspectionForm
from station.models import Fleet_order, Station, Station_inspection, Vehicle_inspection



def station_view(request):    

    """Render the home page."""
    return render(request, "station_base.html")


class report_view(View):

    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)
    
    template_name = "reports.html"

    def get(self, request, station_number):
        active_tab = request.GET.get("tab", "order_report")  # Default to 'order_report'

        # Retrieve start and end dates from the GET request
        start_date_str = request.GET.get('start_date', None)
        end_date_str = request.GET.get('end_date', None)

        # Handle date parsing
        if start_date_str and end_date_str:
            try:
                start_date = timezone.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = timezone.datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                start_date = end_date = timezone.now().date()  # Default to today if parsing fails
        else:
            start_date = end_date = timezone.now().date()  # Default to today if no date provided


        # Initialize context
        context = {
            "station_number": station_number,
            "active_tab": active_tab,
            "start_date": start_date,
            "end_date": end_date,
        }

        # Populate data for the "order_report" tab
        if active_tab == "order_report":
            fleet_orders = Fleet_order.objects.filter(station=station_number, type="fleet",date__range=(start_date, end_date))
            office_orders = Fleet_order.objects.filter(station=station_number, type="office supplies",date__range=(start_date, end_date))

            context["fleet_orders"]=fleet_orders
            context["fleet_total_orders"] = fleet_orders.count()
            context["fleet_pending_orders"] = fleet_orders.filter(status="pending approval").count()
            context["fleet_approved_orders"] = fleet_orders.filter(status="approved").count()
            context["fleet_rejected_orders"] = fleet_orders.filter(status="rejected").count()
            
            context["office_orders"]=office_orders
            context["office_total_orders"] = office_orders.count()
            context["office_pending_orders"] = office_orders.filter(status="pending approval").count()
            context["office_approved_orders"] = office_orders.filter(status="approved").count()
            context["office_rejected_orders"] = office_orders.filter(status="rejected").count()

        elif active_tab == "vehicle_report":
            truck_inspection = Vehicle_inspection.objects.filter(station=station_number,vehicle__vehicle_type='truck',date__range=(start_date, end_date))
            trailer_inspection = Vehicle_inspection.objects.filter(station=station_number,vehicle__vehicle_type='trailer',date__range=(start_date, end_date))

            context["truck_inspection"] = truck_inspection
            context["truck_total_orders"] = truck_inspection.count()
            context["truck_maintenance"] = truck_inspection.filter(type='regular maintenance').count()
            context["truck_repairs"] = truck_inspection.filter(type='repair').count()
            context["truck_inspections"] = truck_inspection.filter(type='inspection').count()

            context["trailer_inspection"] = trailer_inspection
            context["trailer_total_orders"] = trailer_inspection.count()
            context["trailer_maintenance"] = trailer_inspection.filter(type='regular maintenance').count()
            context["trailer_repairs"] = trailer_inspection.filter(type='repair').count()
            context["trailer_inspections"] = trailer_inspection.filter(type='inspection').count()

        elif active_tab == "station_overview":
            context["station1_overview"] = Station_inspection.objects.filter(
                Q(inventory_status="Major inventory issues") | Q(inventory_status="Some tools missing"),
                station=1,
                date__range=(start_date, end_date)
            ).last()
            context["station2_overview"] = Station_inspection.objects.filter(
                Q(inventory_status="Major inventory issues") | Q(inventory_status="Some tools missing"),
                station=2,
                date__range=(start_date, end_date)
            ).last()

        elif active_tab == "station_summary":
            context["station_details"] = Station_inspection.objects.filter(station=station_number,date__range=(start_date, end_date))

        return render(request, self.template_name, context)


class station_inspection_view(View):

    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request,station_number):
        form = StationInspectionForm()
        return render(request, "station_inspection.html", {"form": form, "station_number": station_number})
    
    def post(self, request,station_number):

        form = StationInspectionForm(request.POST)

        if form.is_valid():
            inspection = form.save(commit=False)

            # Handle the inspection date (default to today if not provided)
            selected_date_str = request.POST.get('date')
            if selected_date_str:
                selected_date = timezone.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            else:
                selected_date = timezone.now().date()

            station=Station.objects.get(id=station_number)

            # Assign the selected date to the inspection
            inspection.date = selected_date
            inspection.station = station  
            inspection.saved_on=timezone.now()
            inspection.submitted_by=request.user.username
            inspection.save()

            return redirect('station_inspection', station_number=station_number)
        
        return render(request, "station_inspection.html", {"form": form, "station_number": station_number})


class vehicle_inspection_view(View):

    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, station_number, vehicle):
        form = VehicleInspectionForm(vehicle_type=vehicle)
        Vehicle_inspections=Vehicle_inspection.objects.filter(station=station_number,vehicle__vehicle_type=vehicle)
        return render(request, "vehicle_inspection.html", {"form":form,"station_number": station_number,"vehicle":vehicle, "Vehicle_inspections":Vehicle_inspections})
    
    def post(self, request,station_number,vehicle):

        form = VehicleInspectionForm(request.POST)

        if form.is_valid():
            inspection = form.save(commit=False)

            station=Station.objects.get(id=station_number)

            inspection.station = station
            inspection.saved_on=timezone.now()
            inspection.submitted_by=request.user.username
            inspection.save()

            return redirect('vehicle_inspection', station_number=station_number, vehicle=vehicle)
        

        return render(request, "vehicle_inspection.html", {"form": form, "station_number": station_number,"vehicle":vehicle})
     

class order_view(View):

    permission_classes = [IsAuthenticated]
    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return HttpResponseForbidden("You do not have permission to view this page.")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request,station_number,type):
        form = FleetOrderForm()
        fleet_orders=Fleet_order.objects.filter(type=type, station__id=station_number)
        return render(request, "order.html", {"form":form,"station_number": station_number,"type":type, "fleet_orders":fleet_orders})
    
    def post(self, request,station_number,type):

        form = FleetOrderForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            station=Station.objects.get(id=station_number)

            order.station = station
            order.saved_on=timezone.now()
            order.submitted_by=request.user.username
            order.type=type
            order.save()

            return redirect('order', station_number=station_number, type=type)

        return render(request, "order.html", {"form": form, "station_number": station_number, "type":type})
     