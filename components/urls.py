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
    
    # Supplier URLs
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/<int:pk>/', views.supplier_detail, name='supplier_detail'),
    path('suppliers/add/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:pk>/edit/', views.supplier_update, name='supplier_update'),
    path('suppliers/<int:pk>/delete/', views.supplier_delete, name='supplier_delete'),
    
    # API endpoints
    path('api/description-autocomplete/', views.description_autocomplete, name='description_autocomplete'),
    path('api/manufacturer-autocomplete/', views.manufacturer_autocomplete, name='manufacturer_autocomplete'),
    path('api/supplier-autocomplete/', views.supplier_autocomplete, name='supplier_autocomplete'),
]