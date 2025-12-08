from django.db import models


class ComponentDescription(models.Model):
    """Model to store unique component descriptions for autocomplete."""
    description = models.CharField(max_length=255, unique=True)
    usage_count = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-usage_count', 'description']
    
    def __str__(self):
        return self.description


class ComponentManufacturer(models.Model):
    """Model to store unique component manufacturers for autocomplete."""
    manufacturer = models.CharField(max_length=100, unique=True)
    usage_count = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-usage_count', 'manufacturer']
    
    def __str__(self):
        return self.manufacturer


class ComponentSupplier(models.Model):
    """Model to store unique component suppliers for autocomplete."""
    supplier = models.CharField(max_length=100, unique=True, verbose_name="Supplier Name")
    website = models.URLField(blank=True, null=True, verbose_name="Website")
    contact_email = models.EmailField(blank=True, null=True, verbose_name="Contact Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Phone Number")
    account_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Account Name", help_text="Your account name with this supplier")
    account_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Account Number", help_text="Your account number with this supplier")
    address = models.TextField(blank=True, null=True, verbose_name="Address")
    notes = models.TextField(blank=True, null=True, verbose_name="Notes")
    usage_count = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'supplier']
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
    
    def __str__(self):
        return self.supplier


class Component(models.Model):
    """Model for electronic components with stock management."""
    
    description = models.CharField(
        max_length=255,
        help_text="Description of the component (e.g., 'Resistor', 'Capacitor', etc.)"
    )
    
    value = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Component value if applicable (e.g., '10kΩ', '100μF', '74HC00')"
    )
    
    manufacturer = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Component manufacturer"
    )
    
    supplier_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Supplier name (e.g., 'Digikey', 'Mouser', 'Farnell')"
    )
    
    supplier_part_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Supplier's part number"
    )
    
    supplier_webpage = models.URLField(
        blank=True,
        null=True,
        help_text="Link to supplier's product page"
    )
    
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Unit Cost",
        help_text="Cost per unit (e.g., 0.25, 12.99)"
    )
    
    quantity_in_stock = models.PositiveIntegerField(
        default=0,
        help_text="Number of components currently in stock"
    )
    
    minimum_stock_level = models.PositiveIntegerField(
        default=0,
        help_text="Minimum stock level before reordering"
    )
    
    location = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Storage location (e.g., 'Drawer A1', 'Shelf B2')"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the component"
    )
    
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['description', 'value']
        verbose_name = 'Component'
        verbose_name_plural = 'Components'
    
    def __str__(self):
        if self.value:
            return f"{self.description} - {self.value}"
        return self.description
    
    def save(self, *args, **kwargs):
        # Update or create ComponentDescription for autocomplete
        if self.description:
            description_obj, created = ComponentDescription.objects.get_or_create(
                description=self.description,
                defaults={'usage_count': 1}
            )
            if not created:
                description_obj.usage_count += 1
                description_obj.save()
        
        # Update or create ComponentManufacturer for autocomplete
        if self.manufacturer:
            manufacturer_obj, created = ComponentManufacturer.objects.get_or_create(
                manufacturer=self.manufacturer,
                defaults={'usage_count': 1}
            )
            if not created:
                manufacturer_obj.usage_count += 1
                manufacturer_obj.save()
        
        # Update or create ComponentSupplier for autocomplete
        if self.supplier_name:
            supplier_obj, created = ComponentSupplier.objects.get_or_create(
                supplier=self.supplier_name,
                defaults={'usage_count': 1}
            )
            if not created:
                supplier_obj.usage_count += 1
                supplier_obj.save()
        
        super().save(*args, **kwargs)
    
    @property
    def is_low_stock(self):
        """Check if component stock is below minimum level."""
        return self.quantity_in_stock <= self.minimum_stock_level
    
    @property
    def stock_status(self):
        """Return stock status as a string."""
        if self.quantity_in_stock == 0:
            return "Out of Stock"
        elif self.is_low_stock:
            return "Low Stock"
        else:
            return "In Stock"