from django.urls import path
from .views_customer import customer_dashboard

urlpatterns = [
    path("dashboard/", customer_dashboard, name="customer_dashboard"),
]

