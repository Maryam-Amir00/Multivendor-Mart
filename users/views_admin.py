from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages

from users.models import User
from orders.models import Order

# ------------------------------
# Only admin can access
# ------------------------------
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# ------------------------------
# Admin Dashboard
# ------------------------------
@admin_required
def admin_dashboard(request):
    # Pending vendors
    pending_vendors = User.objects.filter(role="vendor", is_approved=False)

    # All orders
    orders = Order.objects.all().order_by("-created_at")

    # Stats
    total_orders = orders.count()
    paid_orders = orders.filter(is_paid=True).count()
    unpaid_orders = orders.filter(is_paid=False).count()

    context = {
        "pending_vendors": pending_vendors,
        "orders": orders,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "unpaid_orders": unpaid_orders,
    }

    return render(request, "admin_panel/admin_dashboard.html", context)


# ------------------------------
# Approve vendor
# ------------------------------
@admin_required
def approve_vendor(request, user_id):
    user = get_object_or_404(User, id=user_id)

    user.is_approved = True
    user.save()

    messages.success(request, f"Vendor '{user.username}' approved successfully.")
    return redirect("admin_dashboard")


# ------------------------------
# Admin Order Detail
# ------------------------------
@admin_required
def admin_order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    order_items = order.items.all()

    items = []
    total = 0

    for item in order_items:
        subtotal = item.price * item.quantity
        total += subtotal
        items.append({"item": item, "subtotal": subtotal})

    context = {
        "order": order,
        "items": items,
        "order_total": total,
    }

    return render(request, "admin_panel/admin_order_detail.html", context)