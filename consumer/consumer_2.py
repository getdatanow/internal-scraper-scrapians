from confluent_kafka import Consumer, KafkaException
import json
import psycopg2
from config import KAFKA_BROKER, CRAWLED_DATA_TOPIC, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
import base64
import os

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'saver_group',
    'auto.offset.reset': 'earliest'
})

# Initialize PostgreSQL connection
# def get_db_connection():
#     return psycopg2.connect(
#         host=DB_HOST,
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASSWORD
#     )

# Initialize counters
success_count = 0
failure_count = 0

# try:
#     # Try to connect to PostgreSQL
#     conn = get_db_connection()
#     print("Connection successful to DB!")
    
#     # Close the connection
#     conn.close()
# except Exception as e:
#     print(f"Error connecting to PostgreSQL: {e}")

# def save_to_postgres(data, flag):
#     global success_count, failure_count
#     try:
#         conn = get_db_connection()
#         cursor = conn.cursor()
        
#         if flag == "product_details":
#             insert_query = """
#             INSERT INTO product_details (title, price, image_url, product_url) 
#             VALUES (%s, %s, %s, %s);
#             """
#             cursor.execute(insert_query, (data["title"], data["price"], data["image_url"], data["product_url"]))
#             print(f"Data for {data['product_url']} saved to database.")
#             success_count += 1
#         elif flag == "error":
#             insert_query = """
#             INSERT INTO error_url (product_url, remarks) 
#             VALUES (%s, %s);
#             """
#             cursor.execute(insert_query, (data["product_url"], data["remarks"]))
#             print(f"Error for {data['product_url']} saved to database.")
#             failure_count += 1
#         else:
#             pass

#         conn.commit()
#         cursor.close()
#         conn.close()
#     except Exception as e:
#         failure_count += 1
#         print(f"Error saving data to PostgreSQL: {e}")

def generate_filename_from_url(url):
    # Encode the URL to bytes and then Base64 encode it
    base64_encoded = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8')
    
    # Return the Base64-encoded string (without trailing '=' characters)
    return base64_encoded.rstrip("=")

def save_to_json(data, flag):
    # filename = generate_filename_from_url(data['product_url'])
    filename = 'roshankdk'
    print(f'filename: {filename}')
    print(f'data: {data}')
    if flag == "product_details":
        try:
            # Ensure output folder exists
            output_folder = "output"
            os.makedirs(output_folder, exist_ok=True)
            
            # Generate filename
            filename = generate_filename_from_url(data['product_url'])

            file_path = os.path.join(output_folder, filename)
            
            # Save file
            with open(file_path, 'w') as file:
                file.write(data)
            
            print(f"File saved at: {file_path}")
        except Exception as e:
            print(f"failed to save: {e}")
        
        

    if flag == "error":
        pass
    else:
        pass

def consume_messages():
    global success_count, failure_count
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
                    print("consumer 2 entered")
                    save_to_json(message["data"], flag="product_details")
                elif message_type == "error":
                    save_to_json(message["data"], flag="error")
                else:
                    print("Unknown message type")
            except Exception as e:
                failure_count += 1
                print(f"Failed to process message: {e}")
    finally:
        consumer.close()
        print(f"Summary: {success_count} success, {failure_count} failures")

if __name__ == '__main__':
    print("Consumer is now listening for messages on the topic:", CRAWLED_DATA_TOPIC)
    consume_messages()
