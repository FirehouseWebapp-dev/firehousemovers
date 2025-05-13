from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from django.contrib import messages
from inventory_app.permissions import IsManager
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils.crypto import get_random_string
from .forms import PullMaterialForm, ReturnMaterialForm, OrderMaterialForm, OrderReceiptForm
from .models import Material, OrderReceipt
from authentication.models import UserProfile
from authentication.mailer import send_order_email, send_order_status_update_email
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import JsonResponse

class PackagingView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, "packaging_supplies/index.html")

class PullMaterialView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = PullMaterialForm()
        return render(request, "packaging_supplies/pull_material.html", {"form": form})

    def post(self, request):
        form = PullMaterialForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'pull'
            transaction.employee = request.user.userprofile
            transaction.save()
            messages.success(request, "Materials pulled successfully!")
            return redirect("packaging_supplies:index")
        return render(request, "packaging_supplies/pull_material.html", {"form": form})

class ReturnMaterialView(View):
    permission_classes = [IsAuthenticated]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = ReturnMaterialForm()
        return render(request, "packaging_supplies/return_material.html", {"form": form})

    def post(self, request):
        form = ReturnMaterialForm(request.POST)
        print("\n=== DEBUG: Form Validation ===")
        print("Form is valid:", form.is_valid())
        print("POST data:", request.POST)
        
        if form.is_valid():
            # Get the job_id from the form
            job_id = form.cleaned_data['job_id']
            print("\n=== DEBUG: Job ID ===")
            print("Using job_id:", job_id)
            
            trailer_number = form.cleaned_data['trailer_number']
            employee = form.cleaned_data['employee']
            employee_signature = form.cleaned_data['employee_signature']
            
            # Get all pull transactions for this job
            pull_transactions = Material.objects.filter(
                job_id=str(job_id).strip(),
                transaction_type='pull'
            )
            print("\n=== DEBUG: Pull Transactions ===")
            print("Number of pull transactions:", pull_transactions.count())
            
            if not pull_transactions.exists():
                messages.error(request, 'No materials found for this job.')
                return render(request, 'packaging_supplies/return_material.html', {'form': form})
            
            # Calculate total pulled quantities
            total_pulled = {}
            material_fields = [
                'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
                'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
                'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
                'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
                'packing_peanuts', 'ram_board', 'mattress_bags',
                'mirror_cartons', 'bubble_wrap', 'gondola_boxes'
            ]
            
            # Sum up quantities from all pull transactions
            for field in material_fields:
                total_pulled[field] = pull_transactions.aggregate(
                    total=Sum(field)
                )['total'] or 0
            
            # Calculate total already returned quantities
            total_returned = {}
            return_transactions = Material.objects.filter(
                job_id=str(job_id).strip(),
                transaction_type='return'
            )
            
            for field in material_fields:
                total_returned[field] = return_transactions.aggregate(
                    total=Sum(field)
                )['total'] or 0
            
            # Calculate remaining quantities that can be returned
            remaining = {}
            for field in material_fields:
                remaining[field] = total_pulled[field] - total_returned[field]
            
            # Check if this is a summary request
            is_summary_request = 'show_summary' in request.POST
            print("\n=== DEBUG: Request Type ===")
            print("Is summary request:", is_summary_request)
            
            # Get quantities from form data
            quantities = {}
            total_returning = 0
            print("\n=== DEBUG: Processing Quantities ===")
            for field in material_fields:
                # Try to get the quantity from the form data
                quantity = form.cleaned_data.get(field, 0) or 0
                print(f"Original field {field}: {quantity}")
                
                if quantity == 0:
                    # Try the modified field name (without underscores)
                    modified_field = field.replace('_', '')
                    quantity = int(request.POST.get(modified_field, 0)) or 0
                    print(f"Modified field {modified_field}: {quantity}")
                    
                    if quantity == 0:
                        # Try the field name with spaces
                        spaced_field = field.replace('_', ' ')
                        quantity = int(request.POST.get(spaced_field, 0)) or 0
                        print(f"Spaced field {spaced_field}: {quantity}")
                
                quantities[field] = quantity
                total_returning += quantity
                print(f"Final quantity for {field}: {quantity}")
            
            print("\n=== DEBUG: Total Quantities ===")
            print("Total returning:", total_returning)
            
            # Prepare comparison data
            comparison_data = {
                'job_id': job_id,
                'pull_date': pull_transactions.first().date,
                'pull_employee': pull_transactions.first().employee,
                'materials': []
            }
            
            for field in material_fields:
                comparison_data['materials'].append({
                    'name': field.replace('_', ' ').title(),
                    'pulled': total_pulled[field],
                    'already_returned': total_returned[field],
                    'remaining': remaining[field],
                    'returned': quantities[field]
                })
            
            # If this is a summary request
            if is_summary_request:
                print("\n=== DEBUG: Processing Summary Request ===")
                # If no quantities are being returned, show error
                if total_returning == 0:
                    print("No quantities entered, showing error")
                    messages.error(request, 'Please enter quantities to return. No materials are being returned.')
                    return render(request, 'packaging_supplies/return_material.html', {'form': form})
                
                print("Showing summary")
                return render(request, 'packaging_supplies/return_material.html', {
                    'form': form,
                    'comparison_data': comparison_data,
                    'show_summary': True
                })
            
            # If this is a final submission
            print("\n=== DEBUG: Processing Final Submission ===")
            invalid_returns = []
            
            for field in material_fields:
                returned = quantities[field]
                remaining_quantity = remaining[field]
                
                if returned > remaining_quantity:
                    invalid_returns.append(
                        f"{field.replace('_', ' ').title()} "
                        f"(Total Pulled: {total_pulled[field]}, Already Returned: {total_returned[field]}, "
                        f"Remaining: {remaining_quantity}, Trying to Return: {returned})"
                    )
            
            print("\n=== DEBUG: Return Validation ===")
            print("Total returning:", total_returning)
            print("Invalid returns:", invalid_returns)
            
            if invalid_returns:
                messages.error(request, f"Cannot return more than remaining quantities: {', '.join(invalid_returns)}")
                return render(request, 'packaging_supplies/return_material.html', {
                    'form': form,
                    'comparison_data': comparison_data,
                    'show_summary': True
                })
            
            # Check if any quantities are being returned
            if total_returning == 0:
                print("\n=== DEBUG: No Quantities Error ===")
                print("No quantities entered for final submission")
                messages.error(request, 'Please enter quantities to return. No materials are being returned.')
                return render(request, 'packaging_supplies/return_material.html', {
                    'form': form,
                    'comparison_data': comparison_data,
                    'show_summary': True
                })
            
            # Create return record
            return_material = Material.objects.create(
                job_id=job_id,
                trailer_number=trailer_number,
                employee=employee,
                employee_signature=employee_signature,
                transaction_type='return'
            )
            
            # Set material quantities
            for field in material_fields:
                setattr(return_material, field, quantities[field])
            
            return_material.save()
            
            # Create receipt record
            OrderReceipt.objects.create(
                material=return_material,
                date_received=return_material.date.date(),
                uploaded_by=request.user.userprofile
            )
            
            messages.success(request, 'Materials returned successfully.')
            return redirect('packaging_supplies:index')
        else:
            # Print form errors for debugging
            print("\n=== DEBUG: Form Errors ===")
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'packaging_supplies/return_material.html', {
                'form': form,
                'comparison_data': None,
                'show_summary': False
            })

class OrderMaterialView(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = OrderMaterialForm()
        return render(request, "packaging_supplies/order_material.html", {"form": form})

    def post(self, request):
        form = OrderMaterialForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.transaction_type = 'order'
            transaction.employee = request.user.userprofile
            transaction.save()
            
            # Get supplier email from form
            supplier_email = form.cleaned_data['supplier_email']
            
            # Generate status update URLs
            confirm_url = request.build_absolute_uri(
                reverse('packaging_supplies:update_order_status', args=[transaction.id, 'confirmed'])
            )
            reject_url = request.build_absolute_uri(
                reverse('packaging_supplies:update_order_status', args=[transaction.id, 'rejected'])
            )
            
            try:
                # Send email to supplier using the mailer function
                send_order_email(supplier_email, transaction, confirm_url, reject_url)
                messages.success(request, "Order placed successfully and email sent to supplier!")
            except Exception as e:
                messages.warning(request, f"Order placed but email could not be sent: {str(e)}")
            
            # Create receipt record
            OrderReceipt.objects.create(
                material=transaction,
                date_received=transaction.date.date(),
                uploaded_by=request.user.userprofile
            )
            
            return redirect("packaging_supplies:index")
        return render(request, "packaging_supplies/order_material.html", {"form": form})

class OrderReceiptView(View):
    permission_classes = [IsAuthenticated, IsManager]

    def dispatch(self, request, *args, **kwargs):
        for permission in self.permission_classes:
            permission_instance = permission()
            if not permission_instance.has_permission(request, self):
                return redirect("authentication:login")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = OrderReceiptForm()
        receipts = OrderReceipt.objects.all().order_by('-uploaded_at')
        return render(request, "packaging_supplies/order_receipts.html", {
            "form": form,
            "receipts": receipts
        })

    def post(self, request):
        form = OrderReceiptForm(request.POST, request.FILES)
        if form.is_valid():
            receipt = form.save(commit=False)
            receipt.uploaded_by = request.user.userprofile
            receipt.save()
            messages.success(request, "Receipt uploaded successfully!")
            return redirect("packaging_supplies:order_receipts")
        return render(request, "packaging_supplies/order_receipts.html", {"form": form})

@login_required
def index(request):
    # Get current inventory levels
    inventory = {}
    material_fields = [
        'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
        'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
        'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
        'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
        'packing_peanuts', 'ram_board', 'mattress_bags',
        'mirror_cartons', 'bubble_wrap', 'gondola_boxes'
    ]
    
    for field in material_fields:
        pulls = Material.objects.filter(
            transaction_type='pull'
        ).aggregate(total=Sum(field))['total'] or 0
        
        returns = Material.objects.filter(
            transaction_type='return'
        ).aggregate(total=Sum(field))['total'] or 0
        
        orders = Material.objects.filter(
            transaction_type='order'
        ).aggregate(total=Sum(field))['total'] or 0
        
        inventory[field] = orders - (pulls - returns)
    
    # Get recent transactions
    recent_transactions = Material.objects.all().order_by('-date')[:10]
    
    # Get recent receipts
    recent_receipts = OrderReceipt.objects.all().order_by('-date_received')[:10]
    
    context = {
        'inventory': inventory,
        'recent_transactions': recent_transactions,
        'recent_receipts': recent_receipts
    }
    
    return render(request, 'packaging_supplies/index.html', context)

@login_required
def pull_material(request):
    if request.method == 'POST':
        form = PullMaterialForm(request.POST)
        if form.is_valid():
            # Create the pull transaction
            pull_material = form.save(commit=False)
            pull_material.transaction_type = 'pull'
            pull_material.save()
            
            # Create receipt record
            OrderReceipt.objects.create(
                material=pull_material,
                date_received=pull_material.date.date(),
                uploaded_by=request.user.userprofile
            )
            
            messages.success(request, 'Materials pulled successfully.')
            return redirect('packaging_supplies:index')
    else:
        form = PullMaterialForm()
    
    return render(request, 'packaging_supplies/pull_material.html', {'form': form})

@login_required
def record_receipt(request):
    if request.method == 'POST':
        form = OrderReceiptForm(request.POST)
        if form.is_valid():
            date_received = form.cleaned_data['date_received']
            
            # Get all transactions for the selected date
            transactions = Material.objects.filter(
                date__date=date_received
            ).order_by('-date')
            
            # Create receipts for each transaction
            for transaction in transactions:
                OrderReceipt.objects.get_or_create(
                    material=transaction,
                    date_received=date_received,
                    uploaded_by=request.user.userprofile
                )
            
            messages.success(request, 'Receipts recorded successfully!')
            return redirect('packaging_supplies:order_receipts')
    else:
        form = OrderReceiptForm()
    
    # Get all receipts ordered by date
    receipts = OrderReceipt.objects.all().order_by('-date_received', '-uploaded_at')
    
    # If it's an AJAX request, return JSON data
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        date_str = request.GET.get('date')
        if date_str:
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                receipts = OrderReceipt.objects.filter(date_received=date).order_by('-uploaded_at')
            except ValueError:
                receipts = OrderReceipt.objects.none()
        
        receipts_data = []
        for receipt in receipts:
            receipts_data.append({
                'id': receipt.id,
                'date': receipt.date_received.strftime('%b %d, %Y'),
                'job_id': receipt.job_id,
                'type': receipt.transaction_type.title(),
                'trailer': str(receipt.trailer_number),
                'employee': str(receipt.employee),
                'uploaded_by': str(receipt.uploaded_by),
                'quantities': receipt.material_quantities,
                'status': receipt.material.status if receipt.material.transaction_type == 'order' else None
            })
        
        return JsonResponse({'receipts': receipts_data})
    
    return render(request, 'packaging_supplies/order_receipts.html', {
        'form': form,
        'receipts': receipts
    })

@login_required
def return_material(request):
    # Initialize variables
    form = ReturnMaterialForm()
    comparison_data = None
    show_summary = False

    # Handle POST request
    if request.method == 'POST':
        print("\n=== DEBUG: Form Submission ===")
        print("POST data:", request.POST)
        
        form = ReturnMaterialForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            # Process form data
            job_id = form.cleaned_data['job_id']
            trailer_number = form.cleaned_data['trailer_number']
            employee = form.cleaned_data['employee']
            employee_signature = form.cleaned_data['employee_signature']
            
            # Get pull transactions
            pull_transactions = Material.objects.filter(
                job_id=str(job_id).strip(),
                transaction_type='pull'
            )
            
            if not pull_transactions.exists():
                messages.error(request, 'No materials found for this job.')
                return render(request, 'packaging_supplies/return_material.html', {
                    'form': form,
                    'comparison_data': comparison_data,
                    'show_summary': show_summary
                })
            
            # Process material quantities
            material_fields = [
                'small_boxes', 'medium_boxes', 'large_boxes', 'xl_boxes',
                'wardrobe_boxes', 'dish_boxes', 'singleface_protection',
                'carpet_mask', 'paper_pads', 'packing_paper', 'tape',
                'wine_boxes', 'stretch_wrap', 'tie_down_webbing',
                'packing_peanuts', 'ram_board', 'mattress_bags',
                'mirror_cartons', 'bubble_wrap', 'gondola_boxes'
            ]
            
            # Calculate quantities
            total_pulled = {}
            total_returned = {}
            remaining = {}
            quantities = {}
            total_returning = 0
            
            # Calculate pulled quantities
            for field in material_fields:
                total_pulled[field] = pull_transactions.aggregate(
                    total=Sum(field)
                )['total'] or 0
            
            # Calculate returned quantities
            return_transactions = Material.objects.filter(
                job_id=str(job_id).strip(),
                transaction_type='return'
            )
            
            for field in material_fields:
                total_returned[field] = return_transactions.aggregate(
                    total=Sum(field)
                )['total'] or 0
                remaining[field] = total_pulled[field] - total_returned[field]
            
            # Get current return quantities
            print("\n=== DEBUG: Processing Quantities ===")
            for field in material_fields:
                # Try to get the quantity from the form data
                quantity = form.cleaned_data.get(field, 0) or 0
                print(f"Original field {field}: {quantity}")
                
                if quantity == 0:
                    # Try the field name with spaces (title case)
                    spaced_field = field.replace('_', ' ').title()
                    quantity = int(request.POST.get(spaced_field, 0)) or 0
                    print(f"Spaced field {spaced_field}: {quantity}")
                
                quantities[field] = quantity
                total_returning += quantity
                print(f"Final quantity for {field}: {quantity}")
            
            print("\n=== DEBUG: Total Quantities ===")
            print("Total returning:", total_returning)
            
            # Prepare comparison data
            comparison_data = {
                'job_id': job_id,
                'pull_date': pull_transactions.first().date,
                'pull_employee': pull_transactions.first().employee,
                'materials': []
            }
            
            for field in material_fields:
                comparison_data['materials'].append({
                    'name': field.replace('_', ' ').title(),
                    'pulled': total_pulled[field],
                    'already_returned': total_returned[field],
                    'remaining': remaining[field],
                    'returned': quantities[field]
                })
            
            # If this is a final submission
            print("\n=== DEBUG: Processing Final Submission ===")
            invalid_returns = []
            
            for field in material_fields:
                returned = quantities[field]
                remaining_quantity = remaining[field]
                
                if returned > remaining_quantity:
                    invalid_returns.append(
                        f"{field.replace('_', ' ').title()} "
                        f"(Total Pulled: {total_pulled[field]}, Already Returned: {total_returned[field]}, "
                        f"Remaining: {remaining_quantity}, Trying to Return: {returned})"
                    )
            
            print("\n=== DEBUG: Return Validation ===")
            print("Total returning:", total_returning)
            print("Invalid returns:", invalid_returns)
            
            if invalid_returns:
                messages.error(request, f"Cannot return more than remaining quantities: {', '.join(invalid_returns)}")
                return render(request, 'packaging_supplies/return_material.html', {
                    'form': form,
                    'comparison_data': comparison_data,
                    'show_summary': True
                })
            
            # Check if any quantities are being returned
            if total_returning == 0:
                print("\n=== DEBUG: No Quantities Error ===")
                print("No quantities entered for final submission")
                return render(request, 'packaging_supplies/return_material.html', {
                    'form': form,
                    'comparison_data': comparison_data,
                    'show_summary': True
                })
            
            # Create return record
            return_material = Material.objects.create(
                job_id=job_id,
                trailer_number=trailer_number,
                employee=employee,
                employee_signature=employee_signature,
                transaction_type='return'
            )
            
            # Set material quantities
            for field in material_fields:
                setattr(return_material, field, quantities[field])
            
            return_material.save()
            
            # Create receipt record
            OrderReceipt.objects.create(
                material=return_material,
                date_received=return_material.date.date(),
                uploaded_by=request.user.userprofile
            )
            
            messages.success(request, 'Materials returned successfully.')
            return redirect('packaging_supplies:index')
        else:
            print("\n=== DEBUG: Form Errors ===")
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    # Render the form for GET requests or invalid POST requests
    return render(request, 'packaging_supplies/return_material.html', {
        'form': form,
        'comparison_data': comparison_data,
        'show_summary': show_summary
    })

def update_order_status(request, order_id, status):
    """View to handle order status updates via email link"""
    order = get_object_or_404(Material, id=order_id, transaction_type='order')
    
    if status in ['confirmed', 'rejected']:
        order.status = status
        order.save()
        
        try:
            # Send status update email to the employee who placed the order
            send_order_status_update_email(order.employee.user.email, order, status)
            messages.success(request, f'Order has been {status} and notification sent.')
        except Exception as e:
            messages.warning(request, f'Order status updated but notification could not be sent: {str(e)}')
    else:
        messages.error(request, 'Invalid status update.')
    
    # Return a simple HTML response instead of redirecting
    return render(request, 'packaging_supplies/order_status_update.html', {
        'status': status,
        'order': order
    })
