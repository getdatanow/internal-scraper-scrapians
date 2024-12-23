from confluent_kafka import Consumer, Producer, KafkaException
import json
from amazon_crawler import product_details
import psycopg2

KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "urls"
CRAWLED_DATA_TOPIC = "crawled_data"


consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'crawler_group',
    'auto.offset.reset': 'earliest'
})
# Kafka Producer
producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def crawl_url(url):
    try:
        print("Started crawling")
        data = product_details(url)
        if data:
            print(f"Data received:: crawling fininded")

        message = {
            "type": "product_details",
            "data": data,
        }  
    except Exception as e:
        remarks=f"Failed to fetch {url}: {e}"
        data = {
            "product_url":url,
            "remarks": remarks,
        }
        message = {
            "type":"error",
            "data": data,
        }
        print(f"Failed to fetch {url}: {e}")

    # Publish crawled data to the 'crawled_data' topic
    producer.produce(CRAWLED_DATA_TOPIC, json.dumps(message).encode('utf-8'))
    producer.flush()

def consume_messages():
    consumer.subscribe([KAFKA_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            data = json.loads(msg.value().decode('utf-8'))
            print(f'data: {data}')
            url = data['url']
            print(f"FROM COM 1:: Consumed URL : {url}")
            crawl_url(url)
    finally:
        consumer.close()

consume_messages()