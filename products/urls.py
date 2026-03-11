from django.urls import path
from .views import vendor_dashboard
from . import views

urlpatterns = [
    path("", views.product_list, name="product_list"),
    path("<int:pk>/", views.product_detail, name="product_detail"),
    path("vendor/dashboard/", vendor_dashboard, name="vendor_dashboard"),
    # Vendor routes
    path("vendor/", views.vendor_products, name="vendor_products"),
    path("vendor/add/", views.add_product, name="add_product"),
    path("vendor/<int:pk>/edit/", views.edit_product, name="edit_product"),
    path("vendor/<int:pk>/delete/", views.delete_product, name="delete_product"),
    path("vendor/<int:vendor_id>/store/", views.vendor_store, name="vendor_store"),
]
