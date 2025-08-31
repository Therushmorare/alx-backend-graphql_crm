import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import Customer, Product, Order
from django.db import transaction
from django.core.exceptions import ValidationError
import django_filters
from datetime import datetime

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

    class Meta:
        model = Customer
        fields = ["name_icontains", "email_icontains"]

class ProductFilter(django_filters.FilterSet):
    name_icontains = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    low_stock = django_filters.BooleanFilter(method="filter_low_stock")

    class Meta:
        model = Product
        fields = ["name_icontains", "low_stock"]

    def filter_low_stock(self, queryset, name, value):
        if value:
            return queryset.filter(stock__lt=10)
        return queryset

class OrderFilter(django_filters.FilterSet):
    order_date_gte = django_filters.DateFilter(field_name="order_date", lookup_expr="gte")
    order_date_lte = django_filters.DateFilter(field_name="order_date", lookup_expr="lte")

    class Meta:
        model = Order
        fields = ["order_date_gte", "order_date_lte"]

# -----------------------------
# Existing Mutations
# -----------------------------
# Define your CreateCustomer, BulkCreateCustomers, CreateProduct, CreateOrder here
# ... [existing mutations]

# -----------------------------
# Mutation for updating low-stock products
# -----------------------------
class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info):
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_list = []

        for product in low_stock_products:
            product.stock += 10  # Restock by 10
            product.save()
            updated_list.append(ProductType(id=product.id, name=product.name, stock=product.stock))

        return UpdateLowStockProducts(
            updated_products=updated_list,
            message=f"{len(updated_list)} low-stock products updated successfully."
        )

# -----------------------------
# Mutation Class
# -----------------------------
class Mutation(graphene.ObjectType):
    # Existing mutations
    # create_customer = CreateCustomer.Field()
    # bulk_create_customers = BulkCreateCustomers.Field()
    # create_product = CreateProduct.Field()
    # create_order = CreateOrder.Field()

    # Low-stock mutation
    update_low_stock_products = UpdateLowStockProducts.Field()

# -----------------------------
# Query Class
# -----------------------------
class Query(graphene.ObjectType):
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()

