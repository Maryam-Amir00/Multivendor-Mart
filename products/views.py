from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
User = get_user_model()

from products.models import Product
from products.forms import ProductForm
from orders.models import OrderItem


# =====================================================
# PUBLIC PRODUCT LIST
# =====================================================
def product_list(request):
    products = Product.objects.all().order_by("-created_at")
    return render(request, "products/product_list.html", {"products": products})


# =====================================================
# PUBLIC PRODUCT DETAIL
# =====================================================
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "products/product_detail.html", {"product": product})


# =====================================================
# VENDOR PRODUCT LIST (only vendor)
# =====================================================
@login_required
def vendor_products(request):

    if request.user.role != "vendor":
        messages.error(request, "Only vendors can access this page.")
        return redirect("home")

    products = Product.objects.filter(vendor=request.user)
    return render(request, "products/vendor_products.html", {"products": products})


# =====================================================
# ADD A PRODUCT (only approved vendor)
# =====================================================
@login_required
def add_product(request):

    if request.user.role != "vendor":
        messages.error(request, "Only vendors can add products.")
        return redirect("home")

    if not request.user.is_approved:
        messages.error(request, "Your vendor account is not approved yet.")
        return redirect("home")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user
            product.save()
            messages.success(request, "Product added successfully!")
            return redirect("vendor_products")
    else:
        form = ProductForm()

    return render(request, "products/add_product.html", {"form": form})


# =====================================================
# EDIT PRODUCT (only vendor owner)
# =====================================================
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.vendor != request.user:
        messages.error(request, "You cannot edit another vendor’s product.")
        return redirect("vendor_products")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully!")
            return redirect("vendor_products")
    else:
        form = ProductForm(instance=product)

    return render(request, "products/edit_product.html", {
        "form": form,
        "product": product
    })


# =====================================================
# DELETE PRODUCT (only vendor owner)
# =====================================================
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.vendor != request.user:
        messages.error(request, "You cannot delete another vendor’s product.")
        return redirect("vendor_products")

    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("vendor_products")


# =====================================================
# VENDOR DASHBOARD (approved vendors only)
# =====================================================
@login_required
def vendor_dashboard(request):

    if request.user.role != "vendor" or not request.user.is_approved:
        messages.error(request, "Only approved vendors can access the vendor dashboard.")
        return redirect("home")

    vendor = request.user

    # total products this vendor added
    total_products = vendor.products.count()

    # all sold items for this vendor
    sold_items = OrderItem.objects.filter(vendor=vendor)

    # total items sold
    total_sold = sum(item.quantity for item in sold_items)

    # total revenue earned from sold items
    total_revenue = sum(item.price * item.quantity for item in sold_items)

    return render(request, "products/vendor_dashboard.html", {
        "total_products": total_products,
        "total_sold": total_sold,
        "total_revenue": total_revenue,
    })


# =====================================================
# VENDOR STORE (vendor store page)
# =====================================================

def vendor_store(request, vendor_id):
    vendor = get_object_or_404(User, id=vendor_id, role="vendor", is_approved=True)

    products = Product.objects.filter(vendor=vendor).order_by("-created_at")

    return render(request, "products/vendor_store.html", {
        "vendor": vendor,
        "products": products,
    })