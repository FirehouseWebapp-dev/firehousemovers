from django.shortcuts import render
from .forms import InventoryForm, EmployeeForm, UniformAssignmentForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django import forms
from .models import Inventory, Employee, UniformAssignment


def home(request):
    """Render the home page."""
    return render(request, "home.html")


def inventory_list(request):
    """List all inventory items."""
    inventory = Inventory.objects.all()
    return render(request, "inventory_list.html", {"inventory": inventory})


def add_inventory(request):
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
    """Issue uniforms to employees and update inventory."""
    if request.method == "POST":
        form = UniformAssignmentForm(request.POST)
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
        form = UniformAssignmentForm()
    return render(request, "issue_uniform.html", {"form": form})

