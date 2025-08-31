#!/usr/bin/env python3

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

# Configure the GraphQL client
transport = RequestsHTTPTransport(
    url='http://localhost:8000/graphql',
    verify=True,
    retries=3,
)
client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date 7 days ago
seven_days_ago = (datetime.now() - timedelta(days=7)).date()

# GraphQL query to fetch orders in the last 7 days
query = gql("""
query ($startDate: Date!) {
  orders(orderDate_Gte: $startDate) {
    id
    customer {
      email
    }
  }
}
""")

params = {"startDate": str(seven_days_ago)}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])

    log_file = "/tmp/order_reminders_log.txt"

    with open(log_file, "a") as f:
        for order in orders:
            order_id = order["id"]
            email = order["customer"]["email"]
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Order {order_id} for {email}\n")

    print("Order reminders processed!")

except Exception as e:
    print(f"Error fetching orders: {e}")

