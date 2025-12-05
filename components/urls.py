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
    path('api/description-autocomplete/', views.description_autocomplete, name='description_autocomplete'),
    path('api/manufacturer-autocomplete/', views.manufacturer_autocomplete, name='manufacturer_autocomplete'),
    path('api/supplier-autocomplete/', views.supplier_autocomplete, name='supplier_autocomplete'),
]