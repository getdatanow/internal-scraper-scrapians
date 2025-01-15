from confluent_kafka import Consumer, Producer, KafkaException
import json
from config import KAFKA_BROKER, CRAWLED_DATA_TOPIC, KAFKA_URL_TOPIC, MAX_RETRIES, delivery_report
from spider_config import run_multiprocessing

# Configure Kafka consumer
consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'crawler_group',
    'auto.offset.reset': 'earliest'
})

# Initialize Kafka producer
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def crawl_url(url, retry_count):
    """
    Crawls the given URL and publishes the result to Kafka.

    Parameters:
        url (str): The URL to crawl.
        retry_count (int): The current retry attempt.
    """
    try:
        # Attempt crawling the URL using multiprocessing
        print(f"Attempt {retry_count + 1}: Crawling {url}")
        p = run_multiprocessing(url)

        # Uncomment and customize if data retrieval is successful
        # data = start_crawl(url)
        # if data:
        #     message = {
        #         "type": "product_details",
        #         "data": data,
        #     }
        #     producer.produce(CRAWLED_DATA_TOPIC, json.dumps(message).encode('utf-8'), callback=delivery_report)
        #     print(f"Data sent to CONSUMER 2: {message}")
        #     producer.flush()
        #     return

    except Exception as e:
        print(f"Attempt {retry_count + 1}: Failed to crawl {url}. Error: {e}")
        
        if retry_count < MAX_RETRIES - 1:
            # Retry with incremented retry_count
            republish_message(url, retry_count + 1)
        else:
            # Send error message after maximum retries
            remarks = f"Failed to fetch {url} after {MAX_RETRIES} retries: {e}"
            error_message = {
                "type": "error",
                "data": {
                    "product_url": url,
                    "remarks": remarks,
                }
            }
            producer.produce(CRAWLED_DATA_TOPIC, json.dumps(error_message).encode('utf-8'), callback=delivery_report)
            print(f"Max retries reached. Error sent to CONSUMER 1: {error_message}")
            producer.flush()

def republish_message(url, retry_count):
    """
    Republishes a Kafka message with updated retry count.

    Parameters:
        url (str): The URL to republish.
        retry_count (int): The updated retry attempt count.
    """
    message = {
        "url": url,
        "retry_count": retry_count
    }
    producer.produce(KAFKA_URL_TOPIC, json.dumps(message).encode('utf-8'), callback=delivery_report)
    print(f"Retry message published for {url} with retry count {retry_count}")
    producer.flush()

# Kafka message processing logic example
def consume_messages():
    """
    Consumes messages from Kafka and initiates URL crawling.
    """
    consumer.subscribe([KAFKA_URL_TOPIC])
    
    while True:
        msg = consumer.poll(1.0)  # Poll for messages with 1-second timeout
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue

        # Process the message payload
        try:
            data = json.loads(msg.value().decode('utf-8'))
            url = data.get('url')
            retry_count = data.get('retry_count', 0)
            if url:
                crawl_url(url, retry_count)
        except Exception as e:
            print(f"Failed to process message: {msg.value()}. Error: {e}")

if __name__ == '__main__':
    print("Consumer is now listening for messages on the topic:", {KAFKA_URL_TOPIC})
    consume_messages()