from confluent_kafka import Producer
import csv
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "urls"

# Initialize producer
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def read_and_publish(csv_file):
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Print the actual headers to verify they are what we expect
        print(reader.fieldnames)  # This will print the headers from the CSV
        
        for row in reader:
            url = row.get('URL')  # Use 'URL' as it appears in the CSV headers
            if url:
                print(url)  # Process the URL here
            else:
                print("URL column not found for this row.")
            # Send URL as a JSON message to Kafka
            producer.produce(KAFKA_TOPIC, json.dumps({'url': url}), callback=delivery_report)
    
    # Flush the producer after the loop, to send all messages at once
    producer.flush()


# Main function
# def watch_csv_file(csv_file_path):
#     event_handler = FileChangeHandler(csv_file_path)
#     observer = Observer()
#     observer.schedule(event_handler, path=csv_file_path, recursive=False)
#     observer.start()

#     try:
#         print(f"Watching file: {csv_file_path}")
#         while True:
#             time.sleep(1)  # Keep the script running
#     except KeyboardInterrupt:
#         print("Stopping file watcher...")
#         observer.stop()
#     observer.join()
    
# Provide the full path using raw string (r"") to avoid escaping issues
csv_file_path = r"E:\Jyaba\kafka-stack-docker-compose\urls.csv"
read_and_publish(csv_file_path)
