from confluent_kafka import Consumer, Producer, KafkaException
import json
from config import KAFKA_BROKER, CRAWLED_DATA_TOPIC, KAFKA_URL_TOPIC, delivery_report
from pathlib import Path
import sys
import os
import base64
import hashlib
# from kafka import KafkaConsumer

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))
from utility.notification import send_slack_alert
from crawler import asos_crawler


# def generate_filename_from_url(url, extension="json"):
#     # Create a hash for a shorter, unique filename
#     hash_object = hashlib.md5(url.encode('utf-8'))
#     unique_hash = hash_object.hexdigest()
    
#     # Optional: Base64 encode for human readability (if needed)
#     base64_encoded = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8').rstrip("=")
    
#     # Combine base64 and hash for uniqueness and readability
#     filename = f"{base64_encoded[:10]}_{unique_hash[:8]}.{extension}"
    
#     return filename

# def save_to_json(data, url):
#     try:
#         # Ensure output folder exists
#         output_folder = "output"
#         os.makedirs(output_folder, exist_ok=True)
        
#         # Generate filename
#         filename = generate_filename_from_url(url)

#         file_path = os.path.join(output_folder, filename)

#         with open(file_path, 'w', encoding='utf-8') as f:
#             json.dump(data, f, ensure_ascii=False, indent=4)
        
#         print(f"File saved at: {file_path}")
#     except Exception as e:
#         print(f"failed to save: {e}")

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

def save_to_json(data, filename):
    try:
        # Check if file exists and load existing data
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Append new data
        if isinstance(data, list):
            existing_data.extend(data)
        else:
            existing_data.append(data)

        # Write updated data back to the file in JSON format
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        
        print(f"Data successfully saved in JSON format at: {filename}")

    except Exception as e:
        print(f"Failed to save: {e}")

def crawl_url(url):
    try:
        print(f"Started crawling {url}")
        data = asos_crawler.runCrawler(url)
        if data:
            print("Data received succesfully.")
            filename = 'output_asos.json'
            save_to_json(data, filename)
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