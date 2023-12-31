from django.urls import path
from .views import main, add_to_cart, cart, checkout, checkout_proceed, register, sign_in, sign_out, like_product

urlpatterns = [
    path("", main),
    path("sign-up", register, name="sign-up"),
    path("sign-in", sign_in, name="sign-in"),
    path("sign-out", sign_out, name="sign-out"),
    path("add-to-cart/<int:product_id>", add_to_cart, name="add_to_cart"),
    path("cart", cart, name="cart"),
    path("checkout", checkout, name="checkout"),
    path("checkout/procceed", checkout_proceed, name="checkout_proceed"),
    path("like-product", like_product, name="like-product"),

]
