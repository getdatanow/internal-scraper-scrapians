from confluent_kafka import Consumer, KafkaException
import json
import psycopg2
from config import KAFKA_BROKER, CRAWLED_DATA_TOPIC, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'saver_group',
    'auto.offset.reset': 'earliest'
})


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
    print("Connection successful to DB!")
    
    # Close the connection
    conn.close()
except Exception as e:
    print(f"Error connecting to PostgreSQL: {e}")



def save_to_postgres(data, flag):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if flag == "product_details":
            insert_query = """
            INSERT INTO product_details (title, price, image_url, product_url) 
            VALUES (%s, %s, %s, %s);
            """
            cursor.execute(insert_query, (data["title"], data["price"], data["image_url"], data["product_url"]))
            print(f"Data for {data['product_url']} saved to database.")
        elif flag == "error":
            insert_query = """
            INSERT INTO error_url (product_url, remarks) 
            VALUES (%s, %s);
            """
            cursor.execute(insert_query, (data["product_url"], data["remarks"]))
            print(f"Error for {data['product_url']} saved to database.")
        else:
            pass

        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving data to PostgreSQL: {e}")


def consume_messages():
    consumer.subscribe([CRAWLED_DATA_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            
            try:
                message = json.loads(msg.value().decode('utf-8'))
                message_type = message.get("type")
                if message_type == "product_details":
                    save_to_postgres(message["data"], flag="product_details")
                elif message_type == "error":
                    save_to_postgres(message["data"], flag="error")
                else:
                    print("Unknown message type")
            except Exception as e:
                print(f"Failed to process message: {e}")
    finally:
        consumer.close()


if __name__ == '__main__':
    print("Consumer is now listening for messages on the topic:", CRAWLED_DATA_TOPIC)
    consume_messages()
