from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from telegram_bot import post_order_on_telegram
from .models import Order, OrderItems, Coupon
from .forms import NewUserForm
from products.models import Product, LikeProduct
import asyncio


def main(request):
    products = Product.objects.filter(show_on_main_page=True)
    return render(request, "index.html", {"products": products})


def add_to_cart(request, product_id: int):
    product_obj = Product.objects.get(id=product_id)
    is_product_already_exist = False
    if not request.session.get("cart"):
        request.session["cart"] = []
    else:
        for product in request.session.get("cart", []):
            if product_id == product["id"]:
                product["quantity"] = product["quantity"] + 1
                product["price"] = product_obj.price * product["quantity"]
                is_product_already_exist = True

    if not is_product_already_exist:
        request.session["cart"].append({"id": product_id, "quantity": 1, "price": product_obj.price})
    request.session.modified = True
    return HttpResponseRedirect("/")


def cart(request):
    if request.method == "POST":
        coupon_code = request.POST.get("coupon_code")
        request.session["coupon_code"] = coupon_code
        request.session.modified = True

    try:
        code = request.session.get("coupon_code")
        discount = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        discount = None

    cart_products = []
    if not discount or not discount.is_active:
        for cart_item in request.session.get("cart", []):
            product = Product.objects.get(id=cart_item["id"])
            product.quantity = cart_item["quantity"]
            product.total_price = cart_item["price"]
            cart_products.append(product)
    else:
        for cart_item in request.session.get("cart", []):
            product = Product.objects.get(id=cart_item["id"])
            product.quantity = cart_item["quantity"]
            product.total_price = cart_item["price"] * (1 - (discount.discount / 100))
            cart_products.append(product)

    return render(request, "cart.html", {"cart_products": cart_products})


def checkout(request):
    try:
        code = request.session.get("coupon_code")
        discount = Coupon.objects.get(code=code)
    except:
        discount = []

    total_price = 0
    if discount:
        if discount.is_active is False:
            for cart_item in request.session.get("cart", []):
                total_price = total_price + cart_item["price"]

        if not discount.is_active:
            for cart_item in request.session.get("cart", []):
                total_price = total_price + cart_item["price"] * (1 - (discount.discount / 100))

    return render(request, "checkout.html", {"total_price": total_price})


def checkout_proceed(request):
    if request.method == "POST":
        order = Order()
        order.first_name = request.POST.get("first_name")
        order.last_name = request.POST.get("last_name")
        order.email = request.POST.get("email")
        order.address = request.POST.get("address")
        order.address2 = request.POST.get("address2")
        order.country = request.POST.get("country")
        order.city = request.POST.get("city")
        order.postcode = request.POST.get("postcode")
        total = 0
        for item in request.session.get("cart", []):
            total = total + item["price"]
        order.total_price = total
        order.save()
        for item in request.session.get("cart", []):
            order_item = OrderItems()
            order_item.product_id = item["id"]
            order_item.order_id = order.id
            order_item.price = item["price"]
            order_item.quantity = item["quantity"]
            order_item.save()

        order_message = ""
        for item in request.session.get("cart", []):
            product = Product.objects.get(id=item["id"])
            product_name = product.title
            product_quantity = item["quantity"]
            product_price = item["price"]
            item_message = f"{product_name}: \n  Quantity: {product_quantity} \n  Price: {product_price}$"
            order_message += item_message

        order_message = f"Client {order.first_name} {order.last_name}, ordered: \n{order.id}.Order items:\n {order_message}\n"
        asyncio.run(post_order_on_telegram(order_message))
    return HttpResponseRedirect("/")


def like_product(request):
    username = request.user.username
    product_id = request.GET.get('product_id')

    product = Product.objects.get(id=product_id)

    like_filter = LikeProduct.objects.filter(product_id=product_id, username=username).first()

    if like_filter is None:
        new_like = LikeProduct.objects.create(product_id=product_id, username=username)
        new_like.save()
        product.no_of_likes = product.no_of_likes + 1
        product.save()
        return HttpResponseRedirect('/')
    else:
        like_filter.delete()
        product.no_of_likes = product.no_of_likes - 1
        product.save()
        return HttpResponseRedirect('/')


def register(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect("/")
    form = NewUserForm()
    return render(request, "sign-up.html", {"form": form})


def sign_in(request):
    if request.method == "POST":
        user = authenticate(username=request.POST.get("username"), password=request.POST.get("password"))
        if user:
            login(request, user)
        return HttpResponseRedirect('/')
    return render(request, "sign-in.html")


def sign_out(request):
    logout(request)
    return HttpResponseRedirect("/")
