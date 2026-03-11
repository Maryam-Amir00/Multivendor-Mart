def cart_total_qty(request):
    cart = request.session.get("cart", {})
    total_qty = sum(cart.values())
    return {"cart_total_qty": total_qty}
