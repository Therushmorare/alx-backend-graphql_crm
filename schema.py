import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.db import transaction
from datetime import datetime
import re

# -----------------------------
# GraphQL Types
# -----------------------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order


# -----------------------------
# Mutations
# -----------------------------

# 1. CreateCustomer
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        # Validate email uniqueness
        if Customer.objects.filter(email=email).exists():
            raise ValidationError("Email already exists")

        # Validate phone format if provided
        if phone:
            pattern = re.compile(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$')
            if not pattern.match(phone):
                raise ValidationError("Phone format invalid")

        customer = Customer.objects.create(name=name, email=email, phone=phone)
        return CreateCustomer(customer=customer, message="Customer created successfully")


# 2. BulkCreateCustomers
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        for c in input:
            try:
                if Customer.objects.filter(email=c.email).exists():
                    raise ValidationError(f"Email {c.email} already exists")
                if c.phone:
                    pattern = re.compile(r'^(\+\d{10,15}|\d{3}-\d{3}-\d{4})$')
                    if not pattern.match(c.phone):
                        raise ValidationError(f"Phone format invalid for {c.phone}")
                customer = Customer.objects.create(name=c.name, email=c.email, phone=c.phone)
                created_customers.append(customer)
            except ValidationError as e:
                errors.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=errors)


# 3. CreateProduct
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            raise ValidationError("Price must be positive")
        if stock < 0:
            raise ValidationError("Stock cannot be negative")

        product = Product.objects.create(name=name, price=price, stock=stock)
        return CreateProduct(product=product)


# 4. CreateOrder
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.String(required=False)

    order = graphene.Field(OrderType)

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            raise ValidationError("Customer does not exist")

        products = Product.objects.filter(id__in=product_ids)
        if not products:
            raise ValidationError("No valid products selected")

        with transaction.atomic():
            order = Order(customer=customer)
            if order_date:
                order.order_date = datetime.fromisoformat(order_date)
            order.save()  # Save to generate ID for M2M
            order.products.set(products)
            order.total_amount = sum([p.price for p in products])
            order.save()

        return CreateOrder(order=order)


# -----------------------------
# Root Mutation
# -----------------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


# -----------------------------
# Root Query
# -----------------------------
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)

    def resolve_customers(self, info):
        return Customer.objects.all()

    def resolve_products(self, info):
        return Product.objects.all()

    def resolve_orders(self, info):
        return Order.objects.all()
