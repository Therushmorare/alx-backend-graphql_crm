import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# -----------------------------
# Heartbeat Cron Job
# -----------------------------
HEARTBEAT_LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to /tmp/crm_heartbeat_log.txt.
    Queries the GraphQL hello field to verify the endpoint is responsive.
    """
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    # Append heartbeat message
    with open(HEARTBEAT_LOG_FILE, "a") as f:
        f.write(f"{timestamp} CRM is alive\n")

    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Query the hello field
    try:
        query = gql("""
            query {
                hello
            }
        """)
        result = client.execute(query)
        with open(HEARTBEAT_LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL endpoint responsive: {result}\n")
    except Exception as e:
        with open(HEARTBEAT_LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL endpoint check failed: {e}\n")


# -----------------------------
# Low-Stock Restocking Cron Job
# -----------------------------
LOW_STOCK_LOG_FILE = "/tmp/low_stock_updates_log.txt"
GRAPHQL_ENDPOINT = "http://localhost:8000/graphql"

def update_low_stock():
    """
    Runs every 12 hours to update products with stock < 10.
    Executes a GraphQL mutation and logs updates to /tmp/low_stock_updates_log.txt.
    """
    transport = RequestsHTTPTransport(
        url=GRAPHQL_ENDPOINT,
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql("""
    mutation {
        updateLowStockProducts {
            message
            updatedProducts {
                id
                name
                stock
            }
        }
    }
    """)

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result = client.execute(mutation)
        updated_products = result['updateLowStockProducts']['updatedProducts']
        message = result['updateLowStockProducts']['message']

        with open(LOW_STOCK_LOG_FILE, "a") as f:
            f.write(f"{timestamp} - {message}\n")
            for product in updated_products:
                f.write(f"   - {product['name']} (ID: {product['id']}), New Stock: {product['stock']}\n")

        print("Low-stock products updated successfully!")

    except Exception as e:
        with open(LOW_STOCK_LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Error updating low-stock products: {e}\n")
        print("Error occurred:", e)

