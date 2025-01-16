KAFKA_BROKER = "localhost:9092"
KAFKA_URL_TOPIC = "urls"
CRAWLED_DATA_TOPIC = "crawled_data"
MAX_RETRIES = 4

# PostgreSQL configuration
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "root"
DB_PASSWORD = "root"

def delivery_report(err, msg):
    """called when the producer failed to send the message to the consumer listining for message"""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")



import requests
import json

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

def send_slack_alert(message):
    """Send a rich Slack alert with title, color, and attachments"""

    title = "🚨 Alert: Something important happened in the system!"
    color = "#FFA500"

    payload = {
        "text": f"*{title}*",
        "attachments": [
            {
                "text": message,
                "color": color
            }
        ]
    }
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(SLACK_WEBHOOK_URL, data=json.dumps(payload), headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Request failed: {response.status_code}, {response.text}")

