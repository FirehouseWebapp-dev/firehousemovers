from django.shortcuts import render
from .forms import InventoryAssignmentForm, InventoryForm, EmployeeForm, InventoryAssignmentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from .models import Inventory

def home(request):
    permission_classes = [IsAuthenticated]

    """Render the home page."""
    return render(request, "home.html")


def inventory_list(request):
    permission_classes = [IsAuthenticated]
    """List all inventory items."""
    inventory = Inventory.objects.all()
    return render(request, "inventory_list.html", {"inventory": inventory})


def add_inventory(request):
    permission_classes = [IsAuthenticated]

    """Add a new inventory item."""
    if request.method == "POST":
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory_list")
    else:
        form = InventoryForm()
    return render(request, "add_inventory.html", {"form": form})


def add_employee(request):
    permission_classes = [IsAuthenticated]

    """Add a new employee."""
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    else:
        form = EmployeeForm()
    return render(request, "add_employee.html", {"form": form})


def issue_uniform(request):
    permission_classes = [IsAuthenticated]
    
    """Issue uniforms to employees and update inventory."""
    if request.method == "POST":
        form = InventoryAssignmentForm(request.POST)
        if form.is_valid():
            uniform = get_object_or_404(Inventory, pk=form.cleaned_data["uniform"].id)
            quantity = form.cleaned_data["quantity"]
            # Check stock availability
            if form.cleaned_data["condition"] == "new" and uniform.new_stock >= quantity:
                uniform.new_stock -= quantity
            elif form.cleaned_data["condition"] == "used" and uniform.used_stock >= quantity:
                uniform.used_stock -= quantity
            else:
                return JsonResponse({"error": "Insufficient stock."}, status=400)
            # Update in-use stock
            uniform.in_use += quantity
            uniform.save()
            form.save()
            return redirect("inventory_list")
    else:
        form = InventoryAssignmentForm()
    return render(request, "issue_uniform.html", {"form": form})

