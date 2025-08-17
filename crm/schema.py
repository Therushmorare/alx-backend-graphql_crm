import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from datetime import datetime
import django_filters

# -----------------------------
# GraphQL Types
# -----------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

# -----------------------------
# Filters
# -----------------------------
class CustomerFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    email_icontains = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    created_at_gte = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_lte = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")
    phone_pattern = django_filters.CharFilter(method="filter_phone_pattern")

    class Meta:
        model = Customer
        fields = ["name_icontains", "email_icontains", "created_at_gte", "created_at_lte", "phone_pattern"]

    def filter_phone_pattern(self, queryset, name, value):
        return queryset.filter(phone__startswith=value)


class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    price_gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price_lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    stock_gte = django_filters.NumberFilter(field_name="stock", lookup_expr="gte")
    stock_lte = django_filters.NumberFilter(field_name="stock", lookup_expr="lte")
    low_stock = django_filters.BooleanFilter(method="filter_low_stock")

    class Meta:
        model = Product
        fields = ["name_icontains", "price_gte", "price_lte", "stock_gte", "stock_lte", "low_stock"]

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset


class OrderFilter(django_filters.FilterSet):
    total_amount_gte = django_filters.NumberFilter(field_name="total_amount", lookup_expr="gte")
    total_amount_lte = django_filters.NumberFilter(field_name="total_amount", lookup_expr="lte")
    order_date_gte = django_filters.DateFilter(field_name="order_date", lookup_expr="gte")
    order_date_lte = django_filters.DateFilter(field_name="order_date", lookup_expr="lte")
    customer_name = django_filters.CharFilter(field_name="customer__name", lookup_expr="icontains")
    product_name = django_filters.CharFilter(method="filter_by_product_name")
    product_id = django_filters.NumberFilter(method="filter_by_product_id")

    class Meta:
        model = Order
        fields = ["total_amount_gte", "total_amount_lte", "order_date_gte", "order_date_lte", "customer_name", "product_name", "product_id"]

    def filter_by_product_name(self, queryset, name, value):
        return queryset.filter(products__name__icontains=value).distinct()

    def filter_by_product_id(self, queryset, name, value):
        return queryset.filter(products__id=value).distinct()


# -----------------------------
# Mutations (keep your existing ones)
# -----------------------------
# ... [Include your CreateCustomer, BulkCreateCustomers, CreateProduct, CreateOrder classes here] ...


# -----------------------------
# Mutation Class
# -----------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# -----------------------------
# Query Class with Filters
# -----------------------------
class Query(graphene.ObjectType):
    # Filtered connections
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    # Simple list queries
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()
