from django.urls import path
from .views import UserLoginView, custom_logout, customer_dashboard
from . import views

urlpatterns = [
    path("", views.home, name="home"),

    # REGISTER
    path("register/customer/", views.register_customer, name="register_customer"),
    path("register/vendor/", views.register_vendor, name="register_vendor"),

    # AUTH
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", custom_logout, name="user_logout"),

    # DASHBOARD
    path("customer/dashboard/", customer_dashboard, name="customer_dashboard"),
]
