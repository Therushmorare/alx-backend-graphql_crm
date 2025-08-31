#!/bin/bash

python manage.py shell -c "
from datetime import datetime, timedelta
from crm.models import Customer

one_year_ago = datetime.now() - timedelta(days=365)
deleted_count, _ = Customer.objects.filter(last_order__lt=one_year_ago).delete()

print(f'\$(datetime.now().strftime(\"%Y-%m-%d %H:%M:%S\")) - Deleted {deleted_count} inactive customers' >> '/tmp/customer_cleanup_log.txt')
"

