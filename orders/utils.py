def _get_cart(session):
    """
    Returns the cart from session.
    If not present, creates an empty cart dict.
    Cart format: { "product_id": quantity }
    """
    return session.setdefault("cart", {})
