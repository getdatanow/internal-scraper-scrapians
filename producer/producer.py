from confluent_kafka import Producer
import csv
import json
from config import KAFKA_BROKER, KAFKA_TOPIC, CSV_FILE_PATH, delivery_report

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
            message = {
                'url': url,
                'retry_count': 0
            }
            producer.produce(KAFKA_TOPIC, json.dumps(message).encode('utf-8'), callback=delivery_report)
            print(f"Data sent to CONSUMER 1: {message}")
    
    # Flush the producer after the loop, to send all messages at once
    producer.flush()
    
read_and_publish(CSV_FILE_PATH)
