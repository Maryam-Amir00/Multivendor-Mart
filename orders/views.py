from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from products.models import Product
from .models import Order, OrderItem
from .utils import _get_cart

from django.http import JsonResponse
from decimal import Decimal

from django.conf import settings
from django.urls import reverse
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# ----------------------------------------
# ADD TO CART
# ----------------------------------------
@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)

    qty = int(request.POST.get("qty", 1))
    cart = _get_cart(request.session)

    product_id = str(product.id)
    cart[product_id] = cart.get(product_id, 0) + qty
    request.session.modified = True

    messages.success(request, f"{product.name} added to cart!")

    # REDIRECT BASED ON SOURCE
    source = request.POST.get("source")
    if source == "list":
        return redirect("product_list")
    else:
        return redirect("product_detail", pk=pk)


# ----------------------------------------
# REMOVE FROM CART
# ----------------------------------------
def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    pk = str(pk)

    if pk in cart:
        del cart[pk]
        request.session.modified = True

    return redirect("view_cart")


# ----------------------------------------
# VIEW CART
# ----------------------------------------
def view_cart(request):
    cart = request.session.get("cart", {})
    product_ids = cart.keys()

    products = Product.objects.filter(id__in=product_ids)

    cart_items = []
    total = 0

    for product in products:
        qty = cart[str(product.id)]
        subtotal = product.price * qty
        total += subtotal

        cart_items.append({
            "product": product,
            "qty": qty,
            "subtotal": subtotal
        })

    return render(request, "orders/cart.html", {
        "cart_items": cart_items,
        "total": total
    })


# ----------------------------------------
# CHECKOUT (GET + POST + Stripe redirect)
# ----------------------------------------
@login_required
def checkout(request):
    cart = request.session.get("cart", {})

    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect("view_cart")

    # -----------------------------
    # GET — Show summary
    # -----------------------------
    if request.method == "GET":
        product_ids = cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart_items = []
        total = 0

        for product in products:
            qty = cart[str(product.id)]
            subtotal = product.price * qty
            total += subtotal

            cart_items.append({
                "product": product,
                "qty": qty,
                "subtotal": subtotal,
            })

        return render(request, "orders/checkout.html", {
            "cart_items": cart_items,
            "total": total
        })

    # -----------------------------
    # POST — Create order + send to Stripe
    # -----------------------------
    if request.method == "POST":

        # Collect shipping fields
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        email = request.POST.get("email", "").strip()
        country = request.POST.get("country", "").strip()
        city = request.POST.get("city", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()
        street = request.POST.get("street", "").strip()
        apartment = request.POST.get("apartment", "").strip()

        # Required Fields Check
        if not full_name or not phone or not country or not city or not postal_code or not street:
            messages.error(request, "Please fill all required shipping fields.")
            return redirect("checkout")

        # Build full shipping address
        address = f"""
Full Name: {full_name}
Phone: {phone}
Email: {email}
Country: {country}
City: {city}
Postal Code: {postal_code}
Street: {street}
Apartment: {apartment}
""".strip()

        # Create Order
        order = Order.objects.create(
            customer=request.user,
            address=address,
            is_paid=False,
        )

        # Add items to order
        for product_id, qty in cart.items():
            product = Product.objects.get(id=int(product_id))

            if product.stock < qty:
                messages.error(request, f"Not enough stock for {product.name}.")
                order.delete()
                return redirect("checkout")

            OrderItem.objects.create(
                order=order,
                product=product,
                vendor=product.vendor,
                price=product.price,
                quantity=qty
            )

            product.stock -= qty
            product.save()

        # Clear Cart
        request.session["cart"] = {}
        request.session.modified = True

        # Redirect to Stripe Checkout
        return redirect("create_checkout_session", order_id=order.id)


# ----------------------------------------
# ORDER DETAIL
# ----------------------------------------
@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.user != order.customer:
        messages.error(request, "You are not allowed to view this order.")
        return redirect("my_orders")

    order_items = order.items.all()

    items = []
    total = 0

    for item in order_items:
        subtotal = item.price * item.quantity
        total += subtotal
        items.append({"item": item, "subtotal": subtotal})

    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": items,
        "order_total": total,
    })


# ----------------------------------------
# MY ORDERS (customer)
# ----------------------------------------
@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user).order_by("-created_at")

    return render(request, "orders/my_orders.html", {
        "orders": orders
    })


# ----------------------------------------
# VENDOR ORDERS
# ----------------------------------------
@login_required
def vendor_orders(request):
    if request.user.role != "vendor":
        messages.error(request, "Only vendors can view sold items.")
        return redirect("home")

    items = OrderItem.objects.filter(vendor=request.user).order_by("-order__created_at")

    return render(request, "orders/vendor_orders.html", {"items": items})


# ----------------------------------------
# STRIPE CHECKOUT SESSION
# ----------------------------------------


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer=request.user)

    YOUR_DOMAIN = "http://127.0.0.1:8000"

    line_items = []
    for item in order.items.all():  # note related_name 'items'
        # price in cents (Stripe expects integer)
        line_items.append({
            "price_data": {
                "currency": "usd",
                "unit_amount": int(item.price * 100),   # cents
                "product_data": {
                    "name": item.product.name,
                    # optional: include description or metadata inside product_data
                    "description": item.product.description[:200] if item.product.description else None,
                },
            },
            "quantity": int(item.quantity),  # <-- important: pass quantity
        })

    # include the checkout session id in success_url so we can list line items on success page
    success_url = YOUR_DOMAIN + reverse("payment_success", args=[order.id]) + "?session_id={CHECKOUT_SESSION_ID}"
    cancel_url = YOUR_DOMAIN + reverse("payment_cancel")

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        mode="payment",
        line_items=line_items,
        success_url=success_url,
        cancel_url=cancel_url,
    )

    return redirect(checkout_session.url)

# ----------------------------------------
# PAYMENT SUCCESS
# ----------------------------------------
@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer=request.user)

    session_id = request.GET.get("session_id")
    stripe_items = []
    stripe_total = 0

    if session_id:
        try:
            # server-side call (requires secret key)
            line_items = stripe.checkout.Session.list_line_items(session_id, limit=100)
            for li in line_items.data:
                # li contains: price, quantity, description etc.
                product_name = li.description or (li.price.product if hasattr(li.price, "product") else "")
                # prefer fields we know: if li has 'price'->'product'->'name' sometimes nested; fallbacks exist
                # li.amount_subtotal exists if you want raw cents
                stripe_items.append({
                    "description": li.description or li.price.product if li.price else "",
                    "unit_amount": (li.price.unit_amount / 100) if li.price and li.price.unit_amount else None,
                    "quantity": li.quantity,
                    "subtotal": (li.amount_subtotal / 100) if getattr(li, "amount_subtotal", None) else (li.quantity * (li.price.unit_amount / 100) if li.price and li.price.unit_amount else None)
                })
                if getattr(li, "amount_subtotal", None):
                    stripe_total += li.amount_subtotal / 100
                elif li.price and li.price.unit_amount:
                    stripe_total += (li.price.unit_amount * li.quantity) / 100
        except Exception as e:
            # log if you have logging; for now surface a message
            messages.warning(request, "Could not retrieve Stripe line items: " + str(e))

    # mark order paid (if you already marked it via webhook or earlier, consider using webhook instead)
    order.is_paid = True
    order.save()

    # Render a template and show stripe_items & stripe_total
    return render(request, "orders/payment_success.html", {
        "order": order,
        "stripe_items": stripe_items,
        "stripe_total": stripe_total,
    })


# ----------------------------------------
# PAYMENT CANCELLED
# ----------------------------------------
def payment_cancel(request):
    messages.error(request, "Payment was cancelled.")
    return redirect("checkout")



@require_POST
def increase_qty(request, pk):
    """
    Increase product quantity in session cart by 1 (respecting stock).
    Supports AJAX (returns JSON) and normal POST (redirects to view_cart).
    """
    cart = request.session.get("cart", {})
    product = get_object_or_404(Product, pk=pk)
    key = str(pk)

    current = cart.get(key, 0)
    # ensure we do not exceed stock
    if current + 1 > product.stock:
        # Can't increase further
        request.session.modified = True
        messages.error(request, f"Cannot add more than {product.stock} of {product.name}.")
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "max_stock", "max": product.stock}, status=400)
        return redirect("view_cart")

    cart[key] = current + 1
    request.session["cart"] = cart
    request.session.modified = True

    # return JSON for AJAX with new totals
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # recompute totals
        total = Decimal("0.00")
        for pid, qty in cart.items():
            p = Product.objects.get(id=int(pid))
            total += p.price * qty
        subtotal = product.price * cart[key]
        return JsonResponse({
            "ok": True,
            "product_id": key,
            "qty": cart[key],
            "subtotal": str(subtotal),
            "total": str(total)
        })

    messages.success(request, f"Quantity updated for {product.name}.")
    return redirect("view_cart")


@require_POST
def decrease_qty(request, pk):
    """
    Decrease product quantity in session cart by 1.
    If quantity reaches 0, item is removed.
    Supports AJAX and normal POST.
    """
    cart = request.session.get("cart", {})
    key = str(pk)

    if key not in cart:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": "not_in_cart"}, status=400)
        return redirect("view_cart")

    product = get_object_or_404(Product, pk=pk)

    current = cart.get(key, 0)
    new_qty = current - 1

    if new_qty <= 0:
        del cart[key]
    else:
        cart[key] = new_qty

    request.session["cart"] = cart
    request.session.modified = True

    # AJAX response
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        total = Decimal("0.00")
        for pid, qty in cart.items():
            p = Product.objects.get(id=int(pid))
            total += p.price * qty
        subtotal = (product.price * cart[key]) if key in cart else Decimal("0.00")
        return JsonResponse({
            "ok": True,
            "product_id": key,
            "qty": cart.get(key, 0),
            "subtotal": str(subtotal),
            "total": str(total)
        })

    messages.success(request, f"Quantity updated for {product.name}.")
    return redirect("view_cart")