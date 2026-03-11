from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from orders.models import Order

@login_required
def customer_dashboard(request):
    if request.user.role != "customer":
        messages.error(request, "Only customers can access this dashboard.")
        return redirect("home")

    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    total_orders = orders.count()

    # Correct reverse relation
    total_spent = sum(
        sum(item.price * item.quantity for item in order.items.all())
        for order in orders
    )

    return render(request, "dashboard/customer_dashboard.html", {
        "orders": orders,
        "total_orders": total_orders,
        "total_spent": total_spent,
    })
