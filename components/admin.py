from django.contrib import admin
from .models import Component, Event, Tag, JournalEntry


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    """Admin interface for Component model."""
    
    list_display = [
        'description',
        'value',
        'manufacturer',
        'supplier_name',
        'supplier_part_number',
        'cost',
        'quantity_in_stock',
        'stock_status',
        'location',
        'date_added'
    ]
    
    list_filter = [
        'manufacturer',
        'supplier_name',
        'date_added',
        'date_modified'
    ]
    
    search_fields = [
        'description',
        'value',
        'manufacturer',
        'supplier_name',
        'supplier_part_number',
        'location'
    ]
    
    readonly_fields = ['date_added', 'date_modified', 'stock_status']
    
    fieldsets = (
        ('Component Information', {
            'fields': ('description', 'value', 'manufacturer', 'supplier_name', 'supplier_part_number', 'cost')
        }),
        ('Stock Management', {
            'fields': ('quantity_in_stock', 'minimum_stock_level', 'location')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('date_added', 'date_modified', 'stock_status'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        """Display stock status with color coding."""
        status = obj.stock_status
        if status == "Out of Stock":
            return f'<span style="color: red; font-weight: bold;">{status}</span>'
        elif status == "Low Stock":
            return f'<span style="color: orange; font-weight: bold;">{status}</span>'
        else:
            return f'<span style="color: green;">{status}</span>'
    
    stock_status.allow_tags = True
    stock_status.short_description = 'Stock Status'


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """Admin interface for Event model."""
    
    list_display = [
        'title',
        'event_type',
        'start_date',
        'priority',
        'location',
        'completed',
        'created_at'
    ]
    
    list_filter = [
        'event_type',
        'priority',
        'completed',
        'all_day',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'description',
        'location'
    ]
    
    date_hierarchy = 'start_date'
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('title', 'description', 'event_type', 'priority')
        }),
        ('Date & Time', {
            'fields': ('start_date', 'end_date', 'all_day')
        }),
        ('Additional Details', {
            'fields': ('location', 'completed')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model."""
    list_display = ['name']
    search_fields = ['name']


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    """Admin interface for JournalEntry model."""
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    readonly_fields = ['created_at', 'updated_at']