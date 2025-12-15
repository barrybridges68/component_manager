from django.urls import path
from . import views

app_name = 'components'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('components/', views.component_list, name='component_list'),
    path('components/<int:pk>/', views.component_detail, name='component_detail'),
    path('components/add/', views.component_create, name='component_create'),
    path('components/<int:pk>/edit/', views.component_update, name='component_update'),
    path('components/<int:pk>/delete/', views.component_delete, name='component_delete'),
    path('components/export/', views.export_components, name='export_components'),
    path('components/import/', views.import_components, name='import_components'),
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # Todo URLs
    path('todos/', views.todo_list, name='todo_list'),
    path('todos/<int:pk>/', views.todo_detail, name='todo_detail'),
    path('todos/add/', views.todo_create, name='todo_create'),
    path('todos/<int:pk>/edit/', views.todo_update, name='todo_update'),
    path('todos/<int:pk>/delete/', views.todo_delete, name='todo_delete'),
    
    # Purchase Order URLs
    path('purchase-orders/', views.purchase_order_list, name='purchase_order_list'),
    path('purchase-orders/<int:pk>/', views.purchase_order_detail, name='purchase_order_detail'),
    path('purchase-orders/add/', views.purchase_order_create, name='purchase_order_create'),
    path('purchase-orders/<int:pk>/edit/', views.purchase_order_update, name='purchase_order_update'),
    path('purchase-orders/<int:pk>/delete/', views.purchase_order_delete, name='purchase_order_delete'),
    path('components/<int:component_id>/add-to-purchase-order/', views.add_component_to_purchase_order, name='add_component_to_purchase_order'),
    path('purchase-order-items/<int:pk>/edit/', views.purchase_order_item_edit, name='purchase_order_item_edit'),
    path('purchase-order-items/<int:pk>/delete/', views.purchase_order_item_delete, name='purchase_order_item_delete'),
    
    # Calendar
    path('calendar/', views.calendar_view, name='calendar'),
    
    # Event URLs
    path('events/', views.event_list, name='event_list'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/add/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_edit, name='event_edit'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:pk>/toggle-complete/', views.event_toggle_complete, name='event_toggle_complete'),
    
    # Journal URLs
    path('journal/', views.journal_list, name='journal_list'),
    path('journal/<int:pk>/', views.journal_detail, name='journal_detail'),
    path('journal/add/', views.journal_create, name='journal_create'),
    path('journal/<int:pk>/edit/', views.journal_update, name='journal_update'),
    path('journal/<int:pk>/delete/', views.journal_delete, name='journal_delete'),
    
    # API endpoints
    path('api/description-autocomplete/', views.description_autocomplete, name='description_autocomplete'),
    path('api/manufacturer-autocomplete/', views.manufacturer_autocomplete, name='manufacturer_autocomplete'),
    path('api/supplier-autocomplete/', views.supplier_autocomplete, name='supplier_autocomplete'),
]