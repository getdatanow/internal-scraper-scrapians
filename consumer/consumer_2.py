from confluent_kafka import Consumer, KafkaException
import json
import psycopg2

KAFKA_BROKER = "localhost:9092"
CRAWLED_DATA_TOPIC = "crawled_data"

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'saver_group',
    'auto.offset.reset': 'earliest'
})


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

try:
    # Try to connect to PostgreSQL
    conn = get_db_connection()
    print("Connection successful!")
    
    # Close the connection
    conn.close()
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")



def save_to_postgres(data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        insert_query = """
        INSERT INTO product_details (title, price, image_url, product_url) 
        VALUES (%s, %s, %s, %s);
        """
        
        cursor.execute(insert_query, (data["title"], data["price"], data["image_url"], data["product_url"]))

        conn.commit()
        
        cursor.close()
        conn.close()
        print(f"Data for {data['product_url']} saved to database.")
    except Exception as e:
        print(f"Error saving data to PostgreSQL: {e}")


def save_consumer():
    consumer.subscribe([CRAWLED_DATA_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            data = json.loads(msg.value().decode('utf-8'))
            print(data)
            print(f"FROM COM 2:: Consumed crawled data for URL: {data['product_url']}")
            save_to_postgres(data)
    finally:
        consumer.close()


save_consumer()
