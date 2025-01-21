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
    
