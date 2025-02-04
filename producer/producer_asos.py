from confluent_kafka import Producer
# from kafka import KafkaProducer
import csv
import json
from config import KAFKA_BROKER, KAFKA_URL_TOPIC, CSV_FILE_PATH, delivery_report
import os

KAFKA_URL_TOPIC = "urls_asos"
CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output_asos_urls.csv")

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

# producer = KafkaProducer(
#     bootstrap_servers=f"kafka-testing-taraprasad336-d6e1.c.aivencloud.com:19980",
#     security_protocol="SSL",
#     ssl_cafile="ca.pem",
#     ssl_certfile="service.cert",
#     ssl_keyfile="service.key",
# )

sent_url_count = 0
def read_and_publish(csv_file):
    global sent_url_count
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            url = row.get('URL')
            if url:
                # print(url)  # Process the URL here
                pass
            else:
                # print("URL column not found for this row.")
                pass
            # Send URL as a JSON message to Kafka
            message = {
                'url': url,
                'retry_count': 0
            }
            producer.produce(KAFKA_URL_TOPIC, json.dumps(message).encode('utf-8'), callback=delivery_report)
            print(f"Data sent to CONSUMER 1: {message}")
            sent_url_count += 1
    
    # Flush the producer after the loop, to send all messages at once
    producer.flush()

read_and_publish(CSV_FILE_PATH)
