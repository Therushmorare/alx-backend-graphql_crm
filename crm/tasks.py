import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

LOG_FILE = "/tmp/crm_report_log.txt"

from celery import shared_task

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report with total customers, orders, and revenue.
    Logs the report to /tmp/crm_report_log.txt
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Setup GraphQL client
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=3,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)
    
    # GraphQL query for totals
    query = gql("""
    query {
        allCustomers {
            totalCount
        }
        allOrders {
            totalCount
            edges {
                node {
                    totalAmount
                }
            }
        }
    }
    """)
    
    try:
        result = client.execute(query)
        
        total_customers = result['allCustomers']['totalCount']
        total_orders = result['allOrders']['totalCount']
        total_revenue = sum(order['node']['totalAmount'] for order in result['allOrders']['edges'])
        
        # Log report
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, {total_revenue} revenue\n")
        
        print("CRM weekly report generated!")
    
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} - Failed to generate report: {e}\n")
        print("Error generating CRM report:", e)

