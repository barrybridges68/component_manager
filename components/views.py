from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Value, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.db import models
from django.http import JsonResponse
from .models import Component, ComponentDescription, ComponentManufacturer, ComponentSupplier, Todo, PurchaseOrder, PurchaseOrderItem, Event
from .forms import ComponentForm, ComponentSupplierForm, TodoForm, PurchaseOrderForm, PurchaseOrderItemForm, AddToPurchaseOrderForm, PurchaseOrderItemEditForm, EventForm


def component_list(request):
    """Display list of all components with search and filtering."""
    search_query = request.GET.get('search', '')
    
    # Check if any filter parameters exist in the request
    has_filter_params = any(key in request.GET for key in ['in_stock', 'low_stock', 'out_of_stock'])
    
    # Default all filters to checked if no filter params exist
    if has_filter_params:
        status_filters = []
        if request.GET.get('in_stock'):
            status_filters.append('in_stock')
        if request.GET.get('low_stock'):
            status_filters.append('low_stock')
        if request.GET.get('out_of_stock'):
            status_filters.append('out_of_stock')
    else:
        # Default state: all checked
        status_filters = ['in_stock', 'low_stock', 'out_of_stock']
    
    sort_by = request.GET.get('sort', 'description')
    order = request.GET.get('order', 'asc')
    per_page = request.GET.get('per_page', '20')
    
    # Validate per_page parameter
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except ValueError:
        per_page = 20
    
    components = Component.objects.all()
    
    # Handle bulk delete
    if request.method == 'POST' and 'bulk_delete' in request.POST:
        component_ids = request.POST.getlist('component_ids')
        if component_ids:
            deleted_count = Component.objects.filter(id__in=component_ids).count()
            Component.objects.filter(id__in=component_ids).delete()
            messages.success(request, f'Successfully deleted {deleted_count} component(s).')
        return redirect('components:component_list')
    
    if search_query:
        components = components.filter(
            Q(description__icontains=search_query) |
            Q(value__icontains=search_query) |
            Q(manufacturer__icontains=search_query) |
            Q(supplier_name__icontains=search_query) |
            Q(supplier_part_number__icontains=search_query) |
            Q(cost__icontains=search_query)
        )
    
    # Apply status filters (multiple checkboxes)
    if status_filters:
        filter_q = Q()
        if 'out_of_stock' in status_filters:
            filter_q |= Q(quantity_in_stock=0)
        if 'low_stock' in status_filters:
            filter_q |= Q(quantity_in_stock__gt=0, quantity_in_stock__lte=F('minimum_stock_level'))
        if 'in_stock' in status_filters:
            filter_q |= Q(quantity_in_stock__gt=F('minimum_stock_level'))
        components = components.filter(filter_q)
    
    # Apply sorting
    valid_sort_fields = ['description', 'value', 'manufacturer', 'package_type', 'supplier_part_number', 'cost', 'quantity_in_stock', 'location', 'date_added']
    if sort_by in valid_sort_fields:
        if order == 'desc':
            components = components.order_by(f'-{sort_by}')
        else:
            components = components.order_by(sort_by)
    else:
        components = components.order_by('description')
    
    # Pagination
    paginator = Paginator(components, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filters': status_filters,
        'current_sort': sort_by,
        'current_order': order,
        'per_page': per_page,
    }
    return render(request, 'components/component_list.html', context)


def component_detail(request, pk):
    """Display detailed view of a single component."""
    component = get_object_or_404(Component, pk=pk)
    return render(request, 'components/component_detail.html', {'component': component})


def component_create(request):
    """Create a new component."""
    if request.method == 'POST':
        form = ComponentForm(request.POST, request.FILES)
        if form.is_valid():
            component = form.save()
            messages.success(request, f'Component "{component}" has been created successfully.')
            return redirect('components:component_detail', pk=component.pk)
    else:
        form = ComponentForm()
    
    return render(request, 'components/component_form.html', {
        'form': form,
        'title': 'Add New Component'
    })


def component_update(request, pk):
    """Update an existing component."""
    component = get_object_or_404(Component, pk=pk)
    
    if request.method == 'POST':
        # Check if user wants to remove photo or datasheet
        if request.POST.get('remove_photo') == 'true':
            if component.photo:
                component.photo.delete(save=False)
                component.photo = None
                component.save()
                messages.success(request, 'Photo has been removed.')
            return redirect('components:component_update', pk=component.pk)
        
        if request.POST.get('remove_datasheet') == 'true':
            if component.datasheet:
                component.datasheet.delete(save=False)
                component.datasheet = None
                component.save()
                messages.success(request, 'Datasheet has been removed.')
            return redirect('components:component_update', pk=component.pk)
        
        form = ComponentForm(request.POST, request.FILES, instance=component)
        if form.is_valid():
            component = form.save()
            messages.success(request, f'Component "{component}" has been updated successfully.')
            return redirect('components:component_detail', pk=component.pk)
    else:
        form = ComponentForm(instance=component)
    
    return render(request, 'components/component_form.html', {
        'form': form,
        'component': component,
        'title': f'Edit {component}'
    })


def component_delete(request, pk):
    """Delete a component."""
    component = get_object_or_404(Component, pk=pk)
    
    if request.method == 'POST':
        component_name = str(component)
        component.delete()
        messages.success(request, f'Component "{component_name}" has been deleted successfully.')
        return redirect('components:component_list')
    
    return render(request, 'components/component_confirm_delete.html', {'component': component})


def dashboard(request):
    """Display dashboard with stock overview."""
    total_components = Component.objects.count()
    out_of_stock = Component.objects.filter(quantity_in_stock=0).count()
    low_stock = Component.objects.filter(
        quantity_in_stock__gt=0,
        quantity_in_stock__lte=F('minimum_stock_level')
    ).count()
    
    # Calculate total stock cost
    total_stock_cost = 0
    components_with_cost = Component.objects.filter(cost__isnull=False, quantity_in_stock__gt=0)
    for component in components_with_cost:
        total_stock_cost += component.quantity_in_stock * component.cost
    
    # Todo statistics
    uncompleted_todos = Todo.objects.exclude(status='done').count()
    completed_todos = Todo.objects.filter(status='done').count()
    high_priority_todos = Todo.objects.filter(status__in=['pending', 'started', 'blocked'], priority='high').count()
    
    # Purchase order statistics
    total_purchase_orders = PurchaseOrder.objects.count()
    draft_orders = PurchaseOrder.objects.filter(status='draft').count()
    pending_orders = PurchaseOrder.objects.filter(status='pending').count()
    ordered_orders = PurchaseOrder.objects.filter(status='ordered').count()
    
    # Calculate total purchase order value
    total_po_value = 0
    for po in PurchaseOrder.objects.all():
        total_po_value += po.total_amount
    
    recent_components = Component.objects.order_by('-date_added')[:5]
    recent_purchase_orders = PurchaseOrder.objects.select_related('supplier').order_by('-order_date')[:5]
    
    context = {
        'total_components': total_components,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'total_stock_cost': total_stock_cost,
        'uncompleted_todos': uncompleted_todos,
        'completed_todos': completed_todos,
        'high_priority_todos': high_priority_todos,
        'total_purchase_orders': total_purchase_orders,
        'draft_orders': draft_orders,
        'pending_orders': pending_orders,
        'ordered_orders': ordered_orders,
        'total_po_value': total_po_value,
        'recent_components': recent_components,
        'recent_purchase_orders': recent_purchase_orders,
    }
    return render(request, 'components/dashboard.html', context)


def description_autocomplete(request):
    """API endpoint for description autocomplete."""
    query = request.GET.get('q', '')
    if query:
        descriptions = ComponentDescription.objects.filter(
            description__icontains=query
        )[:10].values_list('description', flat=True)
    else:
        descriptions = ComponentDescription.objects.all()[:10].values_list('description', flat=True)
    
    return JsonResponse(list(descriptions), safe=False)


def manufacturer_autocomplete(request):
    """API endpoint for manufacturer autocomplete."""
    query = request.GET.get('q', '')
    if query:
        manufacturers = ComponentManufacturer.objects.filter(
            manufacturer__icontains=query
        )[:10].values_list('manufacturer', flat=True)
    else:
        manufacturers = ComponentManufacturer.objects.all()[:10].values_list('manufacturer', flat=True)
    
    return JsonResponse(list(manufacturers), safe=False)


def supplier_autocomplete(request):
    """API endpoint for supplier autocomplete."""
    query = request.GET.get('q', '')
    if query:
        suppliers = ComponentSupplier.objects.filter(
            supplier__icontains=query
        )[:10].values_list('supplier', flat=True)
    else:
        suppliers = ComponentSupplier.objects.all()[:10].values_list('supplier', flat=True)
    
    return JsonResponse(list(suppliers), safe=False)


def supplier_list(request):
    """Display list of all suppliers with search and filtering."""
    search_query = request.GET.get('search', '')
    sort_by = request.GET.get('sort', 'supplier')
    order = request.GET.get('order', 'asc')
    per_page = request.GET.get('per_page', '20')
    
    # Validate per_page parameter
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except ValueError:
        per_page = 20
    
    # Base queryset
    suppliers = ComponentSupplier.objects.all()
    
    # Search functionality
    if search_query:
        suppliers = suppliers.filter(
            Q(supplier__icontains=search_query) |
            Q(contact_email__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Sorting
    valid_sort_fields = ['supplier', 'contact_email', 'usage_count', 'date_added']
    if sort_by not in valid_sort_fields:
        sort_by = 'supplier'
    
    if order == 'desc':
        sort_by = f'-{sort_by}'
    
    suppliers = suppliers.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(suppliers, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'current_sort': request.GET.get('sort', 'supplier'),
        'current_order': request.GET.get('order', 'asc'),
        'per_page': per_page,
        'total_suppliers': suppliers.count(),
    }
    
    return render(request, 'components/supplier_list.html', context)


def supplier_detail(request, pk):
    """Display details of a specific supplier."""
    supplier = get_object_or_404(ComponentSupplier, pk=pk)
    
    # Get components using this supplier
    components = Component.objects.filter(supplier_name=supplier.supplier)
    
    context = {
        'supplier': supplier,
        'components': components,
        'component_count': components.count(),
    }
    
    return render(request, 'components/supplier_detail.html', context)


def supplier_create(request):
    """Create a new supplier."""
    if request.method == 'POST':
        form = ComponentSupplierForm(request.POST)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.supplier}" was created successfully.')
            return redirect('components:supplier_detail', pk=supplier.pk)
    else:
        form = ComponentSupplierForm()
    
    return render(request, 'components/supplier_form.html', {
        'form': form,
        'title': 'Add New Supplier'
    })


def supplier_update(request, pk):
    """Update an existing supplier."""
    supplier = get_object_or_404(ComponentSupplier, pk=pk)
    
    if request.method == 'POST':
        form = ComponentSupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            supplier = form.save()
            messages.success(request, f'Supplier "{supplier.supplier}" was updated successfully.')
            return redirect('components:supplier_detail', pk=supplier.pk)
    else:
        form = ComponentSupplierForm(instance=supplier)
    
    return render(request, 'components/supplier_form.html', {
        'form': form,
        'supplier': supplier,
        'title': f'Edit {supplier.supplier}'
    })


def supplier_delete(request, pk):
    """Delete a supplier."""
    supplier = get_object_or_404(ComponentSupplier, pk=pk)
    
    if request.method == 'POST':
        supplier_name = supplier.supplier
        supplier.delete()
        messages.success(request, f'Supplier "{supplier_name}" was deleted successfully.')
        return redirect('components:supplier_list')
    
    return render(request, 'components/supplier_confirm_delete.html', {
        'supplier': supplier
    })


# Todo Views
def todo_list(request):
    """Display list of all todos with search and filtering."""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    sort_by = request.GET.get('sort', 'priority')
    order = request.GET.get('order', 'desc')
    per_page = request.GET.get('per_page', '20')
    
    # Validate per_page parameter
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except ValueError:
        per_page = 20
    
    # Base queryset - separate active and completed todos
    active_todos = Todo.objects.exclude(status='done')
    completed_todos = Todo.objects.filter(status='done')
    
    # Search functionality for active todos
    if search_query:
        active_todos = active_todos.filter(
            Q(item__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
        completed_todos = completed_todos.filter(
            Q(item__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Status filter (only apply to active todos since completed are separate)
    if status_filter and status_filter != 'done':
        active_todos = active_todos.filter(status=status_filter)
    
    # Priority filter for both active and completed
    if priority_filter:
        active_todos = active_todos.filter(priority=priority_filter)
        completed_todos = completed_todos.filter(priority=priority_filter)
    
    # Sorting with custom priority ordering for active todos
    valid_sort_fields = ['item', 'priority', 'status', 'date_created', 'completion_date']
    if sort_by not in valid_sort_fields:
        sort_by = 'priority'
    
    # Apply sorting with custom priority order to active todos
    if sort_by == 'priority':
        if order == 'desc':
            # High -> Medium -> Low
            active_todos = active_todos.annotate(
                priority_order=Case(
                    When(priority='high', then=Value(3)),
                    When(priority='medium', then=Value(2)),
                    When(priority='low', then=Value(1)),
                    output_field=IntegerField()
                )
            ).order_by('-priority_order', '-date_created')
        else:
            # Low -> Medium -> High
            active_todos = active_todos.annotate(
                priority_order=Case(
                    When(priority='high', then=Value(3)),
                    When(priority='medium', then=Value(2)),
                    When(priority='low', then=Value(1)),
                    output_field=IntegerField()
                )
            ).order_by('priority_order', '-date_created')
    else:
        if order == 'desc':
            sort_field = f'-{sort_by}'
        else:
            sort_field = sort_by
        active_todos = active_todos.order_by(sort_field)
    
    # Always sort completed todos by completion date (newest first)
    completed_todos = completed_todos.order_by('-completion_date')
    
    # Pagination for active todos only
    paginator = Paginator(active_todos, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status and priority choices for filters (exclude 'done' from status choices for active todos)
    status_choices = [choice for choice in Todo.STATUS_CHOICES if choice[0] != 'done']
    priority_choices = Todo.PRIORITY_CHOICES
    
    context = {
        'page_obj': page_obj,
        'completed_todos': completed_todos[:10],  # Limit completed todos to 10 for performance
        'search_query': search_query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'status_choices': status_choices,
        'priority_choices': priority_choices,
        'current_sort': request.GET.get('sort', 'priority'),
        'current_order': request.GET.get('order', 'desc'),
        'per_page': per_page,
        'total_active_todos': active_todos.count(),
        'total_completed_todos': completed_todos.count(),
    }
    
    return render(request, 'components/todo_list.html', context)


def todo_detail(request, pk):
    """Display details of a specific todo."""
    todo = get_object_or_404(Todo, pk=pk)
    
    context = {
        'todo': todo,
    }
    
    return render(request, 'components/todo_detail.html', context)


def todo_create(request):
    """Create a new todo."""
    if request.method == 'POST':
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save()
            messages.success(request, f'Todo "{todo.item}" was created successfully.')
            return redirect('components:todo_detail', pk=todo.pk)
    else:
        form = TodoForm()
    
    return render(request, 'components/todo_form.html', {
        'form': form,
        'title': 'Add New Todo'
    })


def todo_update(request, pk):
    """Update an existing todo."""
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'POST':
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            todo = form.save()
            messages.success(request, f'Todo "{todo.item}" was updated successfully.')
            return redirect('components:todo_detail', pk=todo.pk)
    else:
        form = TodoForm(instance=todo)
    
    return render(request, 'components/todo_form.html', {
        'form': form,
        'todo': todo,
        'title': f'Edit Todo'
    })


def todo_delete(request, pk):
    """Delete a todo."""
    todo = get_object_or_404(Todo, pk=pk)
    
    if request.method == 'POST':
        todo_item = todo.item
        todo.delete()
        messages.success(request, f'Todo "{todo_item}" was deleted successfully.')
        return redirect('components:todo_list')
    
    return render(request, 'components/todo_confirm_delete.html', {
        'todo': todo
    })


# Purchase Order Views
def purchase_order_list(request):
    """Display list of all purchase orders."""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', 'order_date')
    order = request.GET.get('order', 'desc')
    per_page = request.GET.get('per_page', '20')
    
    # Validate per_page parameter
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 50, 100]:
            per_page = 20
    except ValueError:
        per_page = 20
    
    # Base queryset
    purchase_orders = PurchaseOrder.objects.select_related('supplier')
    
    # Search functionality
    if search_query:
        purchase_orders = purchase_orders.filter(
            Q(order_number__icontains=search_query) |
            Q(supplier__supplier__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Status filter
    if status_filter:
        purchase_orders = purchase_orders.filter(status=status_filter)
    
    # Sorting
    valid_sort_fields = ['order_number', 'supplier__supplier', 'status', 'order_date', 'expected_delivery']
    if sort_by not in valid_sort_fields:
        sort_by = 'order_date'
    
    if order == 'desc':
        sort_by = f'-{sort_by}'
    
    purchase_orders = purchase_orders.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(purchase_orders, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get status choices for filters
    status_choices = PurchaseOrder.STATUS_CHOICES
    
    context = {
        'page_obj': page_obj,
        'purchase_orders': page_obj,  # Add this for template compatibility
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'current_sort': request.GET.get('sort', 'order_date'),
        'current_order': request.GET.get('order', 'desc'),
        'per_page': per_page,
        'total_purchase_orders': purchase_orders.count(),
        'suppliers': ComponentSupplier.objects.all(),  # For filter dropdown
    }
    
    return render(request, 'components/purchase_order_list.html', context)


def purchase_order_detail(request, pk):
    """Display details of a specific purchase order."""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    items = purchase_order.purchaseorderitem_set.select_related('component').all()
    
    context = {
        'purchase_order': purchase_order,
        'items': items,
    }
    
    return render(request, 'components/purchase_order_detail.html', context)


def purchase_order_create(request):
    """Create a new purchase order."""
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            purchase_order = form.save()
            messages.success(request, f'Purchase order "{purchase_order.order_number}" was created successfully.')
            return redirect('components:purchase_order_detail', pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm()
    
    return render(request, 'components/purchase_order_form.html', {
        'form': form,
        'title': 'Create New Purchase Order'
    })


def purchase_order_update(request, pk):
    """Update an existing purchase order."""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        form = PurchaseOrderForm(request.POST, instance=purchase_order)
        if form.is_valid():
            purchase_order = form.save()
            messages.success(request, f'Purchase order "{purchase_order.order_number}" was updated successfully.')
            return redirect('components:purchase_order_detail', pk=purchase_order.pk)
    else:
        form = PurchaseOrderForm(instance=purchase_order)
    
    return render(request, 'components/purchase_order_form.html', {
        'form': form,
        'purchase_order': purchase_order,
        'title': f'Edit Purchase Order {purchase_order.order_number}'
    })


def purchase_order_delete(request, pk):
    """Delete a purchase order."""
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    
    if request.method == 'POST':
        order_number = purchase_order.order_number
        purchase_order.delete()
        messages.success(request, f'Purchase order "{order_number}" was deleted successfully.')
        return redirect('components:purchase_order_list')
    
    return render(request, 'components/purchase_order_confirm_delete.html', {
        'purchase_order': purchase_order
    })


def add_component_to_purchase_order(request, component_id):
    """Add a component to a selected purchase order."""
    component = get_object_or_404(Component, pk=component_id)
    
    if request.method == 'POST':
        form = AddToPurchaseOrderForm(request.POST)
        if form.is_valid():
            purchase_order = form.cleaned_data['purchase_order']
            quantity = form.cleaned_data['quantity']
            unit_cost = form.cleaned_data['unit_cost']
            
            # Check if component already exists in the purchase order
            existing_item = PurchaseOrderItem.objects.filter(
                purchase_order=purchase_order,
                component=component
            ).first()
            
            if existing_item:
                # Update existing item
                existing_item.quantity += quantity
                if unit_cost:
                    existing_item.unit_cost = unit_cost
                existing_item.save()
                messages.success(request, f'Updated quantity for "{component.description}" in purchase order {purchase_order.order_number}.')
            else:
                # Create new item
                PurchaseOrderItem.objects.create(
                    purchase_order=purchase_order,
                    component=component,
                    quantity=quantity,
                    unit_cost=unit_cost or component.cost
                )
                messages.success(request, f'Added "{component.description}" to purchase order {purchase_order.order_number}.')
            
            return redirect('components:purchase_order_detail', pk=purchase_order.pk)
    else:
        initial_data = {}
        if component.cost:
            initial_data['unit_cost'] = component.cost
        form = AddToPurchaseOrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'component': component,
        'title': f'Add {component.description} to Purchase Order'
    }
    
    return render(request, 'components/add_component_to_purchase_order.html', context)


def purchase_order_item_edit(request, pk):
    """Edit a purchase order item's quantity and unit cost."""
    item = get_object_or_404(PurchaseOrderItem, pk=pk)
    purchase_order = item.purchase_order
    
    if request.method == 'POST':
        form = PurchaseOrderItemEditForm(request.POST, instance=item)
        if form.is_valid():
            updated_item = form.save()
            messages.success(request, f'Updated "{updated_item.component.description}" in purchase order {purchase_order.order_number}.')
            return redirect('components:purchase_order_detail', pk=purchase_order.pk)
    else:
        form = PurchaseOrderItemEditForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'purchase_order': purchase_order,
        'title': f'Edit {item.component.description}'
    }
    
    return render(request, 'components/purchase_order_item_edit.html', context)


def purchase_order_item_delete(request, pk):
    """Delete a purchase order item."""
    item = get_object_or_404(PurchaseOrderItem, pk=pk)
    purchase_order = item.purchase_order
    
    if request.method == 'POST':
        component_description = item.component.description
        item.delete()
        messages.success(request, f'Removed "{component_description}" from purchase order {purchase_order.order_number}.')
        return redirect('components:purchase_order_detail', pk=purchase_order.pk)
    
    context = {
        'item': item,
        'purchase_order': purchase_order,
    }
    
    return render(request, 'components/purchase_order_item_confirm_delete.html', context)


def calendar_view(request):
    """Display a weekly or monthly calendar view."""
    from datetime import datetime, date, timedelta
    from collections import defaultdict
    import calendar
    
    # Get view mode (week or month)
    view_mode = request.GET.get('view', 'week')
    today = date.today()
    
    if view_mode == 'month':
        # Get month offset from query parameters
        month_offset = int(request.GET.get('month', 0))
        
        # Calculate target month/year
        target_date = today.replace(day=1) + timedelta(days=32 * month_offset)
        target_date = target_date.replace(day=1)
        
        year = target_date.year
        month = target_date.month
        
        # Get calendar for the month
        cal = calendar.monthcalendar(year, month)
        
        # Get all events for the month
        month_start = date(year, month, 1)
        if month == 12:
            month_end = date(year + 1, 1, 1)
        else:
            month_end = date(year, month + 1, 1)
        
        events = Event.objects.filter(
            start_date__date__gte=month_start,
            start_date__date__lt=month_end
        ).order_by('start_date')
        
        # Group events by date
        events_by_date = defaultdict(list)
        for event in events:
            events_by_date[event.start_date.date()].append(event)
        
        # Create structured data for the template
        calendar_weeks = []
        for week in cal:
            week_data = []
            for day_num in week:
                if day_num == 0:
                    week_data.append(None)
                else:
                    day_date = date(year, month, day_num)
                    week_data.append({
                        'date': day_date,
                        'events': events_by_date.get(day_date, [])
                    })
            calendar_weeks.append(week_data)
        
        context = {
            'view_mode': 'month',
            'calendar_weeks': calendar_weeks,
            'month_name': target_date.strftime('%B %Y'),
            'today': today,
            'prev_month_offset': month_offset - 1,
            'next_month_offset': month_offset + 1,
            'weekdays': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        }
    else:
        # Week view (existing code)
        week_offset = int(request.GET.get('week', 0))
        
        # Calculate the current week start (Monday)
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday) + timedelta(weeks=week_offset)
        
        # Generate the 7 days of the week
        week_days = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            week_days.append(day)
        
        # Get events for this week
        week_end = week_start + timedelta(days=7)
        events = Event.objects.filter(
            start_date__date__gte=week_start,
            start_date__date__lt=week_end
        ).order_by('start_date')
        
        # Group events by date
        events_by_date = defaultdict(list)
        for event in events:
            events_by_date[event.start_date.date()].append(event)
        
        # Create structured data for the template
        calendar_days = []
        for day in week_days:
            calendar_days.append({
                'date': day,
                'events': events_by_date.get(day, [])
            })
        
        # Week range for display
        week_start_str = week_start.strftime('%B %d')
        week_end_str = (week_start + timedelta(days=6)).strftime('%B %d, %Y')
        
        context = {
            'view_mode': 'week',
            'calendar_days': calendar_days,
            'week_start': week_start,
            'week_end': week_start + timedelta(days=6),
            'week_range': f"{week_start_str} - {week_end_str}",
            'today': today,
            'prev_week_offset': week_offset - 1,
            'next_week_offset': week_offset + 1,
        }
    
    return render(request, 'components/calendar.html', context)


def event_list(request):
    """Display list of all events."""
    from datetime import datetime
    
    events = Event.objects.all().order_by('-start_date')
    
    # Filter options
    filter_type = request.GET.get('type', '')
    filter_status = request.GET.get('status', '')
    
    if filter_type:
        events = events.filter(event_type=filter_type)
    
    if filter_status == 'completed':
        events = events.filter(completed=True)
    elif filter_status == 'pending':
        events = events.filter(completed=False)
    
    context = {
        'events': events,
        'filter_type': filter_type,
        'filter_status': filter_status,
        'event_types': Event.EVENT_TYPE_CHOICES,
    }
    
    return render(request, 'components/event_list.html', context)


def event_create(request):
    """Create a new event."""
    from datetime import datetime, date
    
    # Get date from URL parameter if provided
    date_param = request.GET.get('date')
    initial_data = {}
    
    if date_param:
        try:
            parsed_date = datetime.strptime(date_param, '%Y-%m-%d').date()
            initial_data['start_date'] = datetime.combine(parsed_date, datetime.min.time())
        except ValueError:
            pass
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" created successfully!')
            return redirect('components:event_detail', pk=event.pk)
    else:
        form = EventForm(initial=initial_data)
    
    context = {
        'form': form,
        'title': 'Create New Event',
        'submit_text': 'Create Event'
    }
    
    return render(request, 'components/event_form.html', context)


def event_detail(request, pk):
    """Display event details."""
    event = get_object_or_404(Event, pk=pk)
    
    context = {
        'event': event
    }
    
    return render(request, 'components/event_detail.html', context)


def event_edit(request, pk):
    """Edit an existing event."""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            messages.success(request, f'Event "{event.title}" updated successfully!')
            return redirect('components:event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event)
    
    context = {
        'form': form,
        'event': event,
        'title': f'Edit Event: {event.title}',
        'submit_text': 'Update Event'
    }
    
    return render(request, 'components/event_form.html', context)


def event_toggle_complete(request, pk):
    """Toggle event completion status."""
    event = get_object_or_404(Event, pk=pk)
    event.completed = not event.completed
    event.save()
    
    status = "completed" if event.completed else "pending"
    messages.success(request, f'Event "{event.title}" marked as {status}!')
    
    # Redirect to the referrer or event detail
    return redirect(request.META.get('HTTP_REFERER', 'components:event_detail'), pk=event.pk)


def event_delete(request, pk):
    """Delete an event."""
    event = get_object_or_404(Event, pk=pk)
    
    if request.method == 'POST':
        event_title = event.title
        event.delete()
        messages.success(request, f'Event "{event_title}" deleted successfully!')
        return redirect('components:event_list')
    
    context = {
        'event': event
    }
    
    return render(request, 'components/event_confirm_delete.html', context)