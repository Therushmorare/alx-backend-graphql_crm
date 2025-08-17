from crm.models import Customer, Product

# Create sample products
Product.objects.create(name="Laptop", price=1000, stock=10)
Product.objects.create(name="Phone", price=500, stock=20)

# Create sample customers
Customer.objects.create(name="Alice", email="alice@example.com", phone="+1234567890")
Customer.objects.create(name="Bob", email="bob@example.com", phone="123-456-7890")
