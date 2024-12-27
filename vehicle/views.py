from .models import AvailabilityData, Dispatch, Order, Vehicle
from django.views.generic import ListView, FormView
from django.urls import reverse_lazy
from .forms import  DispatchForm, OrderForm, TruckAvailabilityForm
from django.shortcuts import render
from django.views import View
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import redirect


def availability_logistic_view(request):
    """Render the home page."""
    return render(request, "availability_logistic_base.html")
  

class vehicle_availability_view(View):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        trucks = AvailabilityData.objects.filter(vehicle__vehicle_type="truck")
        trailers = AvailabilityData.objects.filter(vehicle__vehicle_type="trailer")
        return render(request, "truck_availability.html", {"trucks": trucks, "trailers": trailers})
    

class JobLogisticsPage(View):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        form1 = OrderForm()
        form2 = DispatchForm()
        job_orders = Order.objects.filter(status='Pending') 
        dispatch = Dispatch.objects.filter(status='Completed') 
        return render(request, "job_logistics.html", {"form":form1,"form2":form2, "job_orders": job_orders,"dispatches": dispatch})
    
    def post(self, request):
        # Initialize both forms without data
        form1 = OrderForm()
        form2 = DispatchForm()

        # Handle OrderForm submission
        if 'submit_order' in request.POST:
            form1 = OrderForm(request.POST)
            if form1.is_valid():
                order = form1.save(commit=False)
                order.saved_by = request.user.username
                order.save()
                return redirect('/job-logistics/')
        
        elif 'submit_dispatch' in request.POST:
            form2 = DispatchForm(request.POST)
            job_orders = Order.objects.filter(status="Pending")  # Fetch pending orders
            dispatches = Dispatch.objects.filter(status='Completed')  # Fetch all dispatches

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
                        

                        # Update status in AvailabilityData for each vehicle by ID
                        for vehicle_id in selected_vehicle_ids:
                            print("vehicle_id: ",vehicle_id)
                            AvailabilityData.objects.filter(vehicle__id=vehicle_id).update(status='Out of Service')

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


    
class logistic_report(View):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return render(request, "logistic_report.html")
    


class availability_report(View):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return render(request, "availability_report.html")
