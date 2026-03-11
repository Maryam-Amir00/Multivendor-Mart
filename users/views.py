from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.db import IntegrityError
from orders.models import Order
from products.models import Product
from django.contrib.auth.decorators import login_required

from .forms import CustomerSignUpForm, VendorSignUpForm


def home(request):
    products = Product.objects.all().order_by("-created_at")[:8]  # show latest 8
    return render(request, "home.html", {"products": products})


# ------------------------------------------------------------
# CUSTOMER REGISTRATION
# ------------------------------------------------------------
def register_customer(request):
    if request.method == "POST":
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                form.add_error("username", "This username is already taken.")
                return render(request, "users/register.html", {"form": form, "role": "customer"})
            
            login(request, user)
            messages.success(request, "Welcome! You are now registered and logged in.")
            return redirect("home")
        # if form invalid, fall down and re-render
    else:
        form = CustomerSignUpForm()

    return render(request, "users/register.html", {"form": form, "role": "customer"})


# ------------------------------------------------------------
# VENDOR REGISTRATION
# ------------------------------------------------------------
def register_vendor(request):
    if request.method == "POST":
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
            except IntegrityError:
                form.add_error("username", "This username is already taken.")
                return render(request, "users/register.html", {"form": form, "role": "vendor"})
            
            messages.success(request, "Vendor account created! Wait for admin approval.")
            return redirect("login")

    else:
        form = VendorSignUpForm()

    return render(request, "users/register.html", {"form": form, "role": "vendor"})


# ------------------------------------------------------------
# LOGIN VIEW — vendor approval check
# ------------------------------------------------------------
class UserLoginView(LoginView):
    template_name = "users/login.html"

    def form_valid(self, form):
        user = form.get_user()

        # Block unapproved vendors
        if user.role == "vendor" and not user.is_approved:
            messages.error(self.request, "Your vendor account is not approved yet.")
            return redirect("login")

        # Log user in
        login(self.request, user)

        # Redirect admin
        if user.is_superuser or user.is_staff:
            return redirect("admin_dashboard")

        # Redirect vendor
        if user.role == "vendor":
            return redirect("vendor_dashboard")

        # Redirect customer
        if user.role == "customer":
            return redirect("customer_dashboard")

        # Fallback
        return redirect("home")



# ------------------------------------------------------------
# LOGOUT
# ------------------------------------------------------------
def custom_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("login")

# ------------------------------------------------------------
# CUSTOMER DASHBOARD
# ------------------------------------------------------------
@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        messages.error(request, "Only customers can access this dashboard.")
        return redirect("home")

    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    total_orders = orders.count()

    return render(request, "dashboard/customer_dashboard.html", {
        "total_orders": total_orders,
        "cart_total_qty": request.session.get("cart", {}),
    })
