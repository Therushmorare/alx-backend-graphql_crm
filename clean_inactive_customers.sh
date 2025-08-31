#!/bin/bash

# Run Django shell to delete customers with no orders in the last year
deleted_count=$(python3 manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer, Order

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True) | Customer.objects.exclude(order__date__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")

# Log the deleted count with timestamp
echo \"\$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers\" >> /tmp/customer_cleanup_log.txt
