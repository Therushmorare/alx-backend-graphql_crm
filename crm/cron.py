import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to /tmp/crm_heartbeat_log.txt.
    Queries the GraphQL hello field to verify the endpoint is responsive.
    """
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    
    # Append heartbeat message
    with open(LOG_FILE, "a") as f:
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
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL endpoint responsive: {result}\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL endpoint check failed: {e}\n")

