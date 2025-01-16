from confluent_kafka import Consumer, Producer, KafkaException
import json
from config import KAFKA_BROKER, CRAWLED_DATA_TOPIC, KAFKA_URL_TOPIC, delivery_report, send_slack_alert
from pathlib import Path
import sys
import os
import base64
# from kafka import KafkaConsumer

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from crawler import amazon_crawler


def generate_filename_from_url(url):
    # Encode the URL to bytes and then Base64 encode it
    base64_encoded = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8')
    
    # Return the Base64-encoded string (without trailing '=' characters)
    return base64_encoded.rstrip("=")

def save_to_json(data):
    try:
        # Ensure output folder exists
        output_folder = "output"
        os.makedirs(output_folder, exist_ok=True)
        
        # Generate filename
        filename = generate_filename_from_url(data['product_url'])
        
        if filename:
            file_path = os.path.join(output_folder, filename)
        else:
            file_path = os.path.join(output_folder, data['product_url'])
        
        # Save file
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        
        print(f"File saved at: {file_path}")
    except Exception as e:
            print(f"failed to save: {e}")



# consumer configuration 
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'crawler_group',
    'auto.offset.reset': 'earliest'
})
# consumer = KafkaConsumer(
#     KAFKA_URL_TOPIC,
#     bootstrap_servers=f"kafka-testing-taraprasad336-d6e1.c.aivencloud.com:19980",
#     client_id = "CONSUMER_CLIENT_ID",
#     group_id = "CONSUMER_GROUP_ID",
#     security_protocol="SSL",
#     ssl_cafile="ca.pem",
#     ssl_certfile="service.cert",
#     ssl_keyfile="service.key",
# )

def crawl_url(url):
    try:
        print(f"Started crawling {url}")
        data = amazon_crawler.runCrawler(url)
        if data:
            print("Data received succesfully.")
            save_to_json(data)
            return
    except Exception as e:
        print(f"Failed to fetch {url}. Error: {e}")
        # triger to send alert in slack
        alert_msg = f"Failed to fetch {url}. Error: {e}"
        try:
            send_slack_alert(alert_msg)
        except Exception as e:
            print(f"Failed to send ALERT: {e}")

def consume_messages():
    consumer.subscribe([KAFKA_URL_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            data = json.loads(msg.value().decode('utf-8'))
            url = data.get('url')
            print(f"Consumed message: {data}")
            crawl_url(url)
    finally:
        consumer.close()

if __name__ == '__main__':
    print("Consumer is now listening for messages on the topic:", {KAFKA_URL_TOPIC})
    consume_messages()