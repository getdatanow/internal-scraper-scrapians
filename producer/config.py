KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "urls"

# Provide the full path using raw string (r"") to avoid escaping issues
# csv_file_path = r"E:\Jyaba\kafka-stack-docker-compose\urls.csv"
csv_file_path = r"E:\Jyaba\kafka-stack-docker-compose\urls.csv"


def delivery_report(err, msg):
    """called when the producer failed to send the message to the consumer listining for message"""
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")