from django import forms
from .models import Component, ComponentSupplier, Todo, PurchaseOrder, PurchaseOrderItem, Event


class ComponentForm(forms.ModelForm):
    """Form for creating and updating components."""
    
    class Meta:
        model = Component
        fields = [
            'description',
            'value',
            'manufacturer',
            'supplier_name',
            'supplier_part_number',
            'supplier_webpage',
            'cost',
            'quantity_in_stock',
            'minimum_stock_level',
            'location',
            'package_type',
            'notes'
        ]
        widgets = {
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Resistor, Capacitor, IC',
                'list': 'description-suggestions',
                'autocomplete': 'off',
                'required': True
            }),
            'value': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 10kΩ, 100μF, 74HC00'
            }),
            'manufacturer': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Texas Instruments, Vishay',
                'list': 'manufacturer-suggestions',
                'autocomplete': 'off'
            }),
            'supplier_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Digikey, Mouser, Farnell',
                'list': 'supplier-suggestions',
                'autocomplete': 'off'
            }),
            'supplier_part_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Supplier part number'
            }),
            'supplier_webpage': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/product-page'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': 'e.g., 1.25, 0.50'
            }),
            'quantity_in_stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'minimum_stock_level': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Drawer A1, Shelf B2'
            }),
            'package_type': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., SMD 0805, Through-hole, DIP-14, SOIC-8',
                'list': 'package-type-suggestions',
                'autocomplete': 'off'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this component'
            }),
        }


class ComponentSupplierForm(forms.ModelForm):
    """Form for creating and updating suppliers."""
    
    class Meta:
        model = ComponentSupplier
        fields = [
            'supplier',
            'website',
            'contact_email',
            'phone_number',
            'account_name',
            'account_number',
            'address',
            'notes'
        ]
        widgets = {
            'supplier': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Digikey, Mouser, Farnell'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.supplier-website.com'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@supplier.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 555-123-4567'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your company name'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your account number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Supplier address'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this supplier'
            }),
        }


class TodoForm(forms.ModelForm):
    """Form for creating and updating todo items."""
    
    class Meta:
        model = Todo
        fields = [
            'item',
            'priority',
            'status',
            'notes'
        ]
        widgets = {
            'item': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter todo item description',
                'required': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or details'
            }),
        }


class PurchaseOrderForm(forms.ModelForm):
    """Form for creating and updating purchase orders."""
    
    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier',
            'status',
            'expected_delivery',
            'notes'
        ]
        widgets = {
            'supplier': forms.Select(attrs={
                'class': 'form-select'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'expected_delivery': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes for this purchase order'
            }),
        }


class PurchaseOrderItemForm(forms.ModelForm):
    """Form for adding items to purchase orders."""
    
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'component',
            'quantity',
            'unit_cost',
            'notes'
        ]
        widgets = {
            'component': forms.Select(attrs={
                'class': 'form-select'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Notes for this item'
            }),
        }


class AddToPurchaseOrderForm(forms.Form):
    """Form for adding a component to a selected purchase order."""
    
    purchase_order = forms.ModelChoiceField(
        queryset=PurchaseOrder.objects.filter(status__in=['draft', 'pending']),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text="Select a purchase order to add this component to"
    )
    
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'value': '1'
        }),
        help_text="Quantity to add to the purchase order"
    )
    
    unit_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'min': '0'
        }),
        help_text="Unit cost (leave blank to use component's default cost)"
    )


class PurchaseOrderItemEditForm(forms.ModelForm):
    """Form for editing purchase order item quantities and costs."""
    
    class Meta:
        model = PurchaseOrderItem
        fields = ['quantity', 'unit_cost']
        widgets = {
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'unit_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
        }
        labels = {
            'quantity': 'Quantity',
            'unit_cost': 'Unit Cost ($)',
        }
        help_texts = {
            'quantity': 'Enter the quantity needed.',
            'unit_cost': 'Enter the cost per unit.',
        }


class EventForm(forms.ModelForm):
    """Form for creating and updating calendar events."""
    
    class Meta:
        model = Event
        fields = [
            'title',
            'description',
            'event_type',
            'start_date',
            'end_date',
            'all_day',
            'priority',
            'location',
            'completed'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter event title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional event details (optional)'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'required': True
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'all_day': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Event location (optional)'
            }),
            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'title': 'Event Title',
            'description': 'Description',
            'event_type': 'Event Type',
            'start_date': 'Start Date & Time',
            'end_date': 'End Date & Time',
            'all_day': 'All Day Event',
            'priority': 'Priority',
            'location': 'Location',
            'completed': 'Mark as Completed',
        }
        
        help_texts = {
            'title': 'Enter a descriptive title for your event.',
            'description': 'Provide additional details about the event.',
            'start_date': 'When does the event start?',
            'end_date': 'When does the event end? (Leave blank for no end time)',
            'all_day': 'Check if this is an all-day event.',
            'location': 'Where is the event taking place?',
        }