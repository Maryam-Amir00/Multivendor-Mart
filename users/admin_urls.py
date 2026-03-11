from django.urls import path
from .views_admin import admin_dashboard, approve_vendor, admin_order_detail

urlpatterns = [
    path("dashboard/", admin_dashboard, name="admin_dashboard"),
    path("approve/<int:user_id>/", approve_vendor, name="approve_vendor"),
    path("orders/<int:pk>/", admin_order_detail, name="admin_order_detail"),
]
