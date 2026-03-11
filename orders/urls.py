from django.urls import path
from .views import (
    add_to_cart,
    remove_from_cart,
    view_cart,
    checkout,
    increase_qty,
    decrease_qty,
    order_detail,
    my_orders,
    vendor_orders,
    create_checkout_session,
    payment_success,
    payment_cancel,
)

urlpatterns = [
    # CART
    path("add/<int:pk>/", add_to_cart, name="add_to_cart"),
    path("remove/<int:pk>/", remove_from_cart, name="remove_from_cart"),
    path("", view_cart, name="view_cart"),

    # QUANTITY UPDATE
    path("cart/increase/<int:pk>/", increase_qty, name="increase_qty"),
    path("cart/decrease/<int:pk>/", decrease_qty, name="decrease_qty"),

    # CHECKOUT + PAYMENT
    path("checkout/", checkout, name="checkout"),
    path("payment/<int:order_id>/pay/", create_checkout_session, name="create_checkout_session"),
    path("payment/success/<int:order_id>/", payment_success, name="payment_success"),
    path("payment/cancel/", payment_cancel, name="payment_cancel"),

    # ORDERS
    path("orders/<int:pk>/", order_detail, name="order_detail"),
    path("my-orders/", my_orders, name="my_orders"),
    path("vendor-orders/", vendor_orders, name="vendor_orders"),
]
