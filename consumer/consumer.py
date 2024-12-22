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


# -------------------------------------------------------------------
# PostgreSQL configuration
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "root"
DB_PASSWORD = "root"


# Initialize PostgreSQL connection
def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def save_error_url(url, remarks):
    try:
        # Save the URL into the 'error_url' table
        conn = get_db_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO error_url (product_url, remarks) 
        VALUES (%s, %s);
        """
        
        cursor.execute(insert_query, (url, remarks))
        conn.commit()
        
        cursor.close()
        conn.close()
        print(f"Failed URL {url} saved to error_url table.")
    except Exception as e:
        print(f"Error saving failed URL {url} to PostgreSQL: {e}")
# -------------------------------------------------------------------

def crawl_url(url):
    try:
        print("Started crawling")
        data = product_details(url)
        print(f"Data received:: crawling fininded")
        # Publish crawled data to the 'crawled_data' topic
        producer.produce(CRAWLED_DATA_TOPIC, json.dumps(data).encode('utf-8'))
        producer.flush()
        print(f"Published crawled data to {CRAWLED_DATA_TOPIC}")
    except Exception as e:
        remarks=f"Failed to fetch {url}: {e}"
        save_error_url(url, remarks)
        print(f"Failed to fetch {url}: {e}")

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
            url = data['url']
            print(f"FROM COM 1:: Consumed URL : {url}")
            crawl_url(url)
    finally:
        consumer.close()

consume_messages()