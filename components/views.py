from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F, Sum, Value
from django.db.models.functions import Coalesce
from django.db import models
from django.http import JsonResponse
from .models import Component, ComponentDescription, ComponentManufacturer, ComponentSupplier
from .forms import ComponentForm


def component_list(request):
    """Display list of all components with search and filtering."""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
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
    
    # Apply status filter
    if status_filter == 'out_of_stock':
        components = components.filter(quantity_in_stock=0)
    elif status_filter == 'low_stock':
        components = components.filter(
            quantity_in_stock__gt=0,
            quantity_in_stock__lte=F('minimum_stock_level')
        )
    elif status_filter == 'in_stock':
        components = components.filter(quantity_in_stock__gt=F('minimum_stock_level'))
    
    # Apply sorting
    valid_sort_fields = ['description', 'value', 'manufacturer', 'supplier_name', 'supplier_part_number', 'cost', 'quantity_in_stock', 'location', 'date_added']
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
        'status_filter': status_filter,
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
        form = ComponentForm(request.POST)
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
        form = ComponentForm(request.POST, instance=component)
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
    
    recent_components = Component.objects.order_by('-date_added')[:5]
    
    context = {
        'total_components': total_components,
        'out_of_stock': out_of_stock,
        'low_stock': low_stock,
        'total_stock_cost': total_stock_cost,
        'recent_components': recent_components,
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