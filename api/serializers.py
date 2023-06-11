from rest_framework import serializers
from products.models import Product, Category
from main.models import Order, OrderItems


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "description", "price", "discount_price"]


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    products = ProductSerializer(read_only=True, many=True)

    class Meta:
        model = Category
        fields = ["id", "title", "slug", "products"]


class OrderItemSerializer(serializers.HyperlinkedModelSerializer):
    products = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItems
        fields = ["id", "products", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(read_only=True, many=True)

    class Meta:
        model = Order
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'address2', 'country', 'city', 'postcode',
                  'total_price', 'items']
