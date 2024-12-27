KAFKA_BROKER = "localhost:9092"
KAFKA_URL_TOPIC = "urls"
CRAWLED_DATA_TOPIC = "crawled_data"
MAX_RETRIES = 4

# PostgreSQL configuration
DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "root"
DB_PASSWORD = "root"

def delivery_report(err, msg):
    """called when the producer failed to send the message to the consumer listining for message"""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")