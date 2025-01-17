
from confluent_kafka import Consumer, Producer, KafkaException
import json
from config import KAFKA_BROKER, KAFKA_URL_TOPIC
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utility import scrapy_runner

# Configure Kafka consumer
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'crawler_group',
    'auto.offset.reset': 'earliest'
})

def crawl_url(url):
    """
    Crawls the given URL and publishes the result to Kafka.

    Parameters:
        url (str): The URL to crawl.
    """
    try:
        # Attempt crawling the URL using multiprocessing
        print(f"Started Crawling for: {url}")
        p = scrapy_runner.run_multiprocessing(url)
    except Exception as e:
        print(f"Failed to crawl {url}. Error: {e}")


# Kafka message processing logic example
def consume_messages():
    """
    Consumes messages from Kafka and initiates URL crawling.
    """
    consumer.subscribe([KAFKA_URL_TOPIC])
    try:
        while True:
            msg = consumer.poll(1.0)  # Poll for messages with 1-second timeout
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            
            data = json.loads(msg.value().decode('utf-8'))
            url = data.get('url')
            print(f"Consumed message: {url}")
            if url:
                crawl_url(url)
    except Exception as e:
        print(f"Consumer error: {e}")

if __name__ == '__main__':
    print("Consumer is now listening for messages on the topic:", {KAFKA_URL_TOPIC})
    consume_messages()
