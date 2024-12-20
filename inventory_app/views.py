from django.shortcuts import render
from .forms import InventoryForm, EmployeeForm, UniformAssignmentForm,SignUpForm
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views import View
from .models import Inventory, Employee, UniformAssignment
from django.contrib import messages


def check_email_availability(request):
    email = request.GET.get("email", None)
    data = {"is_taken": User.objects.filter(email__iexact=email).exists()}
    return JsonResponse(data)

class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, "signup.html", {"form": form})

    def post(self, request):
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.cleaned_data.get("first_name")
            email = form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                request.session.flush()
                messages.error(
                    request, "Email already exists. Please choose another one."
                )
                return render(request, "signup.html", {"form": form})
        return render(request, "signup.html", {"form": form})


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

