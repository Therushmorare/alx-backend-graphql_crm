import datetime
import requests
import logging

LOG_FILE = "/tmp/crm_heartbeat_log.txt"

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to /tmp/crm_heartbeat_log.txt.
    Optionally checks the GraphQL endpoint for responsiveness.
    """
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    
    # Append message to the log file
    with open(LOG_FILE, "a") as f:
        f.write(message)

    # Optional: check GraphQL endpoint
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ hello }"},
            timeout=5
        )
        if response.status_code == 200:
            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint responsive\n")
        else:
            with open(LOG_FILE, "a") as f:
                f.write(f"{timestamp} GraphQL endpoint returned status {response.status_code}\n")
    except Exception as e:
        with open(LOG_FILE, "a") as f:
            f.write(f"{timestamp} GraphQL endpoint check failed: {e}\n")

