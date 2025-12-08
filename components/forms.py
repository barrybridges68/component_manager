from django import forms
from .models import Component, ComponentSupplier


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