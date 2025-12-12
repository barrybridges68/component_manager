from django.db import models
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
import os
from datetime import datetime


def component_photo_path(instance, filename):
    """Generate unique path for component photos with timestamp."""
    ext = os.path.splitext(filename)[1]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{instance.description}_{timestamp}{ext}"
    return os.path.join('component_photos', new_filename)


def component_datasheet_path(instance, filename):
    """Generate unique path for component datasheets with timestamp."""
    ext = os.path.splitext(filename)[1]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{instance.description}_{timestamp}{ext}"
    return os.path.join('component_datasheets', new_filename)


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
    
    package_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Package type (e.g., 'SMD 0805', 'Through-hole', 'DIP-14', 'SOIC-8')"
    )
    
    photo = models.ImageField(
        upload_to=component_photo_path,
        blank=True,
        null=True,
        help_text="Photo of the component"
    )
    
    datasheet = models.FileField(
        upload_to=component_datasheet_path,
        blank=True,
        null=True,
        help_text="Datasheet PDF for the component"
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
        # If updating, delete old files if new ones are uploaded
        if self.pk:
            try:
                old_instance = Component.objects.get(pk=self.pk)
                if old_instance.photo and self.photo and old_instance.photo != self.photo:
                    if os.path.isfile(old_instance.photo.path):
                        os.remove(old_instance.photo.path)
                if old_instance.datasheet and self.datasheet and old_instance.datasheet != self.datasheet:
                    if os.path.isfile(old_instance.datasheet.path):
                        os.remove(old_instance.datasheet.path)
            except Component.DoesNotExist:
                pass
        
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
    
    def delete(self, *args, **kwargs):
        """Delete component and associated files."""
        # Delete photo file if it exists
        if self.photo:
            if os.path.isfile(self.photo.path):
                os.remove(self.photo.path)
        
        # Delete datasheet file if it exists
        if self.datasheet:
            if os.path.isfile(self.datasheet.path):
                os.remove(self.datasheet.path)
        
        super().delete(*args, **kwargs)
    
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


class Todo(models.Model):
    """Model for todo items with priority and status tracking."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('started', 'Started'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]
    
    item = models.CharField(
        max_length=255,
        help_text="Description of the todo item"
    )
    
    date_created = models.DateTimeField(
        default=timezone.now,
        help_text="Date when the todo was created"
    )
    
    completion_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date when the todo was completed"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Priority level of the todo item"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text="Current status of the todo item"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes or details about the todo"
    )
    
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', '-date_created']
        verbose_name = 'Todo Item'
        verbose_name_plural = 'Todo Items'
    
    def __str__(self):
        return f"{self.item} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Automatically set completion date when status changes to 'done'
        if self.status == 'done' and not self.completion_date:
            self.completion_date = timezone.now()
        # Clear completion date if status changes from 'done' to something else
        elif self.status != 'done' and self.completion_date:
            self.completion_date = None
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if todo is overdue (created more than 7 days ago and not done)."""
        if self.status == 'done':
            return False
        return (timezone.now() - self.date_created).days > 7
    
    @property
    def priority_badge_class(self):
        """Return Bootstrap badge class based on priority."""
        priority_classes = {
            'high': 'bg-danger',
            'medium': 'bg-warning text-dark',
            'low': 'bg-secondary'
        }
        return priority_classes.get(self.priority, 'bg-secondary')
    
    @property
    def status_badge_class(self):
        """Return Bootstrap badge class based on status."""
        status_classes = {
            'pending': 'bg-secondary',
            'started': 'bg-primary',
            'blocked': 'bg-danger',
            'done': 'bg-success'
        }
        return status_classes.get(self.status, 'bg-secondary')


class PurchaseOrder(models.Model):
    """Model for purchase orders."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]
    
    order_number = models.CharField(
        max_length=20,
        unique=True,
        help_text="Purchase order number"
    )
    
    supplier = models.ForeignKey(
        ComponentSupplier,
        on_delete=models.CASCADE,
        help_text="Supplier for this purchase order"
    )
    
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the purchase order"
    )
    
    order_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date when the order was created"
    )
    
    expected_delivery = models.DateField(
        blank=True,
        null=True,
        help_text="Expected delivery date"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes for the purchase order"
    )
    
    date_modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-order_date']
        verbose_name = 'Purchase Order'
        verbose_name_plural = 'Purchase Orders'
    
    def __str__(self):
        return f"PO-{self.order_number} - {self.supplier.supplier}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number if not provided
            last_order = PurchaseOrder.objects.order_by('-id').first()
            if last_order and last_order.order_number.startswith('PO'):
                try:
                    last_num = int(last_order.order_number[2:])
                    self.order_number = f"PO{last_num + 1:04d}"
                except ValueError:
                    self.order_number = f"PO{timezone.now().year}{timezone.now().month:02d}001"
            else:
                self.order_number = f"PO{timezone.now().year}{timezone.now().month:02d}001"
        super().save(*args, **kwargs)
    
    @property
    def total_amount(self):
        """Calculate total amount of the purchase order."""
        total = 0
        for item in self.purchaseorderitem_set.all():
            if item.unit_cost and item.quantity:
                total += item.unit_cost * item.quantity
        return total
    
    @property
    def item_count(self):
        """Get count of items in the purchase order."""
        return self.purchaseorderitem_set.count()
    
    @property
    def status_badge_class(self):
        """Return Bootstrap badge class based on status."""
        status_classes = {
            'draft': 'bg-secondary',
            'pending': 'bg-warning text-dark',
            'ordered': 'bg-primary',
            'received': 'bg-success',
            'cancelled': 'bg-danger'
        }
        return status_classes.get(self.status, 'bg-secondary')


class PurchaseOrderItem(models.Model):
    """Model for individual items in a purchase order."""
    
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        help_text="Purchase order this item belongs to"
    )
    
    component = models.ForeignKey(
        Component,
        on_delete=models.CASCADE,
        help_text="Component to order"
    )
    
    quantity = models.PositiveIntegerField(
        help_text="Quantity to order"
    )
    
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Unit cost for this order (may differ from component cost)"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes for this specific item"
    )
    
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['purchase_order', 'component']
        ordering = ['component__description']
    
    def __str__(self):
        return f"{self.component.description} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        # Set unit cost from component if not provided
        if not self.unit_cost and self.component.cost:
            self.unit_cost = self.component.cost
        super().save(*args, **kwargs)
    
    @property
    def total_cost(self):
        """Calculate total cost for this line item."""
        if self.unit_cost and self.quantity:
            return self.unit_cost * self.quantity
        return 0


class Event(models.Model):
    """Model for calendar events."""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    EVENT_TYPE_CHOICES = [
        ('meeting', 'Meeting'),
        ('delivery', 'Delivery'),
        ('deadline', 'Deadline'),
        ('maintenance', 'Maintenance'),
        ('order', 'Order Due'),
        ('reminder', 'Reminder'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(
        max_length=200,
        help_text="Event title or description"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Additional event details"
    )
    
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='other',
        help_text="Type of event"
    )
    
    start_date = models.DateTimeField(
        help_text="Event start date and time"
    )
    
    end_date = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Event end date and time (optional)"
    )
    
    all_day = models.BooleanField(
        default=False,
        help_text="Is this an all-day event?"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        help_text="Event priority level"
    )
    
    location = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Event location"
    )
    
    # Link to related objects (optional)
    related_component = models.ForeignKey(
        'Component',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Related component (if applicable)"
    )
    
    related_purchase_order = models.ForeignKey(
        'PurchaseOrder',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Related purchase order (if applicable)"
    )
    
    related_supplier = models.ForeignKey(
        'ComponentSupplier',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        help_text="Related supplier (if applicable)"
    )
    
    # Tracking fields
    completed = models.BooleanField(
        default=False,
        help_text="Mark as completed"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_date', 'title']
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
    
    def __str__(self):
        return f"{self.title} - {self.start_date.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_overdue(self):
        """Check if event is overdue and not completed."""
        return not self.completed and self.start_date < timezone.now()
    
    @property
    def duration_hours(self):
        """Calculate event duration in hours."""
        if self.end_date:
            delta = self.end_date - self.start_date
            return delta.total_seconds() / 3600
        return 0
    
    @property
    def priority_badge_class(self):
        """Return Bootstrap badge class based on priority."""
        priority_classes = {
            'low': 'bg-secondary',
            'medium': 'bg-warning text-dark',
            'high': 'bg-danger'
        }
        return priority_classes.get(self.priority, 'bg-secondary')
    
    @property
    def type_badge_class(self):
        """Return Bootstrap badge class based on event type."""
        type_classes = {
            'meeting': 'bg-info',
            'delivery': 'bg-success',
            'deadline': 'bg-danger',
            'maintenance': 'bg-warning text-dark',
            'order': 'bg-primary',
            'reminder': 'bg-secondary',
            'other': 'bg-dark'
        }
        return type_classes.get(self.event_type, 'bg-dark')


class Tag(models.Model):
    """Model for tags that can be applied to journal entries."""
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Tag name"
    )
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class JournalEntry(models.Model):
    """Model for journal entries with automatic timestamps."""
    
    title = models.CharField(
        max_length=200,
        help_text="Title or subject of the journal entry"
    )
    
    content = models.TextField(
        help_text="Journal entry content"
    )
    
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='journal_entries',
        help_text="Tags for categorizing this entry"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Journal Entry'
        verbose_name_plural = 'Journal Entries'
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"