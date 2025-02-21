from collections import defaultdict
from django.shortcuts import render, redirect
from rest_framework.permissions import IsAuthenticated
from django.views import View
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from authentication.models import UserProfile
from inventory_app.forms import (
    AddEmployeeForm,
    InventoryForm,
    UniformCatalogForm,
    UniformIssueForm,
)
from inventory_app.models import (
    Inventory,
    InventoryTransaction,
    UniformAssignment,
    UniformCatalog,
)
from datetime import datetime
from django.contrib import messages
from inventory_app.permissions import IsManager
from django.contrib.auth.decorators import login_required


@login_required(login_url='authentication:login')
def uniform_inventory_view(request):
    """Render the home page."""
    return render(request, "inventory_base.html")


def homeview(request):
    """Render the home page."""
    return render(request, "home.html")


class Add_uniform_view(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect('authentication:login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = UniformCatalogForm()

        return render(
            request,
            "add_uniform.html",
            {
                "form": form,
            },
        )

    def post(self, request):
        form = UniformCatalogForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Uniform Added Successfully!")
        else:
            messages.error(request, form.errors)
        return render(request, "inventory_base.html", {"form": form})


class Return_uniform_view(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect('authentication:login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        employees = UserProfile.objects.all()
        uniforms = []
        return render(
            request,
            "return_uniform.html",
            {"employees": employees, "uniforms": uniforms},
        )

    def post(self, request):
        employees = UserProfile.objects.all()
        employee_id = request.POST.get("employee")
        uniform_id = request.POST.get("uniform")

        try:
            employee = UserProfile.objects.get(id=employee_id)
            uniform_catalog = UniformCatalog.objects.get(id=uniform_id)
            # Retrieve the active uniform assignment
            uniform = UniformAssignment.objects.filter(
                employee=employee, status="Active", uniform=uniform_catalog
            ).first()

            if uniform:
                # Create a new "Returned" uniform assignment
                UniformAssignment.objects.create(
                    date=datetime.now(),
                    employee=employee,
                    uniform=uniform.uniform,
                    status="Returned",
                    condition=uniform.condition,
                    quantity=uniform.quantity,
                )

                # Update any relevant uniforms or return information
                uniforms = UniformAssignment.objects.filter(
                    employee=employee, status="Active"
                )
                messages.success(request, "Uniform Returned Successfully!")
                return render(
                    request,
                    "inventory_base.html",
                    {"employees": employees, "uniforms": uniforms},
                )
            else:
                messages.error(request, "Failed to Return Uniform!")
                return HttpResponseForbidden(
                    "No active uniform found for this employee."
                )

        except UserProfile.DoesNotExist:
            return HttpResponseForbidden("Employee not found.")
        except UniformCatalog.DoesNotExist:
            return HttpResponseForbidden("Uniform not found.")


def get_uniforms(request):
    employee_id = request.GET.get("employee_id")

    if employee_id:
        try:
            # Get the employee record
            employee = UserProfile.objects.get(id=employee_id)

            # Step 1: Get all uniform assignments for the employee
            all_uniforms = UniformAssignment.objects.filter(employee=employee)

            # Step 2: Create a dictionary to hold the latest uniform assignment for each uniform type
            latest_uniforms = {}

            for uniform in all_uniforms:
                uniform_id = uniform.uniform.id
                # For each uniform type, check if this is the latest assignment (most recent based on the 'id' sequence)
                if (
                    uniform_id not in latest_uniforms
                    or latest_uniforms[uniform_id].id < uniform.id
                ):
                    latest_uniforms[uniform_id] = uniform

            # Step 3: Prepare the return list with only the active uniforms
            active_uniforms = []
            for uniform in latest_uniforms.values():
                # Only include uniforms that are "Active"
                if uniform.status == "Active":
                    active_uniforms.append(
                        {
                            "id": uniform.uniform.id,
                            "name": str(uniform.uniform),
                            "condition": uniform.condition,
                            "quantity": uniform.quantity,
                            "date_assigned": uniform.date,
                        }
                    )

            # Return the list of active uniforms
            return JsonResponse({"uniforms": active_uniforms})

        except UserProfile.DoesNotExist:
            return JsonResponse({"error": "Employee not found"}, status=404)
    else:
        return JsonResponse({"error": "Employee ID not provided"}, status=400)


class Issue_uniform_view(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect('authentication:login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = UniformIssueForm()
        return render(
            request,
            "issue_uniform.html",
            {
                "form": form,
            },
        )

    def post(self, request):
        form = UniformIssueForm(request.POST)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.date = datetime.now()
            assignment.status = "Active"
            assignment.save()
            messages.success(request, "Uniform Assigned Successfully!")
            return redirect("inventory")
        else:
            messages.error(request, form.errors)
        return render(request, "issue_uniform.html", {"form": form})


class Employee_view(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect('authentication:login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = AddEmployeeForm()
        employees = UserProfile.objects.all()

        return render(request, "employee.html", {"form": form, "employees": employees})

    def post(self, request):
        action = request.POST.get(
            "action"
        )  # This checks whether we're adding or deleting

        if action == "delete":
            # Handle the deletion of an employee
            employee_id = request.POST.get("employee")
            if employee_id:
                try:
                    emp = UserProfile.objects.get(id=employee_id)

                    # Delete the associated User instance
                    user = emp.user
                    emp.delete()
                    user.delete()
                    messages.success(request, "Employee Deleted Successfully!")

                    return redirect("employee")
                except UserProfile.DoesNotExist:
                    pass
            else:
                messages.error(request, "Failed to  Delete Employee!")

            return redirect("employee")

        # If action is not delete, then add employee
        form = AddEmployeeForm(request.POST)
        if form.is_valid():
            # Creating User instance (use a default email and password)
            user = User.objects.create_user(
                username=form.cleaned_data["name"],
                email="default@example.com",
                password="defaultpassword123",
            )

            # Now create the UserProfile and associate it with the user
            user_profile = form.save(commit=False)
            user_profile.user = user
            user_profile.save()

            messages.success(request, "Employee Added Successfully!")
            return redirect("employee")
        else:
            messages.error(request, form.errors)
            employees = UserProfile.objects.all()
            return render(
                request, "employee.html", {"form": form, "employees": employees}
            )

    def delete(self, request):
        employee_id = request.POST.get("employee")
        if employee_id:
            try:
                emp = UserProfile.objects.get(id=employee_id)
                emp.delete()
                return redirect("inventory")
            except UserProfile.DoesNotExist:
                return HttpResponseForbidden("Employee not found.")
        return redirect("employee")


class inventory_view(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect('authentication:login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = InventoryForm()

        if "inventory-remove" in request.path:
            template_name = "remove_inventory.html"
        else:
            template_name = "add_inventory.html"

        return render(
            request,
            template_name,
            {
                "form": form,
            },
        )

    def post(self, request):
        form = InventoryForm(request.POST)
        template = ""

        if form.is_valid():
            # Extract cleaned data from the form
            uniform = form.cleaned_data["uniform"].id
            quantity = form.cleaned_data["quantity"]
            condition = form.cleaned_data["condition"]
            transaction_type = form.cleaned_data["transaction_type"]
            notes = form.cleaned_data["notes"]

            # Get or create the inventory for the selected uniform
            uniform = UniformCatalog.objects.get(id=uniform)
            inventory, created = Inventory.objects.get_or_create(uniform=uniform)
            in_use_uniforms = UniformAssignment.objects.filter(
                uniform=uniform, status="Active"
            ).count()
            inventory.uniform = uniform

            if "inventory-remove" in request.path:
                template = "remove_inventory.html"

                if condition == "New":
                    inventory.new_stock = max((inventory.new_stock or 0) - quantity, 0)
                else:
                    inventory.used_stock = max(
                        (inventory.used_stock or 0) - quantity, 0
                    )
                if transaction_type == "Dispose":
                    inventory.disposed = (inventory.disposed or 0) + quantity

                else:
                    inventory.return_to_supplier = (
                        inventory.return_to_supplier or 0
                    ) + quantity
                    inventory.total_bought = max(
                        (inventory.total_bought or 0) - quantity, 0
                    )

                new_in_use = in_use_uniforms - quantity
                if new_in_use < 0:
                    new_in_use = 0
                inventory.in_use = new_in_use

                messages.success(request, "Inventory Deleted Successfully!")
            else:
                transaction_type = "Purchase"
                template = "add_inventory.html"
                if condition == "New":
                    inventory.new_stock = (inventory.new_stock or 0) + quantity
                else:
                    inventory.used_stock = (inventory.used_stock or 0) + quantity

                inventory.total_bought = (inventory.total_bought or 0) + quantity
                inventory.in_use = in_use_uniforms + quantity

                messages.success(request, "Inventory Added Successfully!")

            InventoryTransaction.objects.create(
                transaction_type=transaction_type,
                notes=notes,
                date=datetime.now(),
                uniform=uniform,
                quantity=quantity,
                condition=condition,
            )
            inventory.save()

            return redirect("inventory")
        else:
            messages.success(request, form.errors)
            template = "add_inventory.html"
        return render(request, template, {"form": form})


class Reports_view(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        # Manually check permissions before executing the view logic
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect('authentication:login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, "reports.html")

    def post(self, request):
        inventory_summary = request.POST.get("employee")
        if inventory_summary == "inventory_summary":
            inventory_records = Inventory.objects.all()
            return render(
                request, "reports.html", {"inventory_records": inventory_records}
            )
        else:
            uniform_assignments = UniformAssignment.objects.filter(status="Active")
            employee_data = defaultdict(lambda: defaultdict(int))

            # Group and sum uniform quantities by employee and uniform
            for assignment in uniform_assignments:
                employee_data[assignment.employee][
                    assignment.uniform.name
                ] += assignment.quantity

            employee_data = {
                employee: dict(uniforms) for employee, uniforms in employee_data.items()
            }

            return render(request, "reports.html", {"employee_data": employee_data})
