from confluent_kafka import Consumer, Producer, KafkaException
import json
from config import KAFKA_BROKER, CRAWLED_DATA_TOPIC, KAFKA_URL_TOPIC, MAX_RETRIES, delivery_report
from pathlib import Path
import sys
import os
import multiprocessing
from scrapy.crawler import CrawlerProcess

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from crawler import bellician_spider

consumer = Consumer({
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'crawler_group',
    'auto.offset.reset': 'earliest'
})

producer = Producer({'bootstrap.servers': KAFKA_BROKER})

def worker(url_queue):
    while not url_queue.empty():
        url = url_queue.get()
        process = CrawlerProcess()
        print(f"url is: {url}")
        process.crawl(bellician_spider.BellicianSpider, url=url)
        process.start()

def run_multiprocessing(urls):
    url_queue = multiprocessing.Queue()

    # for url in urls:
    #     url_queue.put(url)

    url_queue.put(urls)

    processes = []
    num_workers = 2  # Use multiple workers (adjust as needed)
    
    # Create worker processes
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(url_queue,))
        processes.append(p)
        p.start()  # Start each worker process

    # Wait for all processes to finish
    for p in processes:
        p.join()
        

def crawl_url(url, retry_count):
    try:
        print(f"Attempt {retry_count + 1}: Started crawling {url}")
        
        # run the spider with os.system // second option
        # os.system(f"scrapy runspider E:\\Jyaba\\kafka-stack-docker-compose\\crawler\\bellician_spider.py -a url={url}")

        # run the spider with the multiprocessing // first option
        p = run_multiprocessing(url)


        # get the data from the spider
        # data = start_crawl(url)
        # if data:
        #     print("Data successfully fetched.")
        #     message = {
        #         "type": "product_details",
        #         "data": data,
        #     }
        #     # Publish successful message to crawled_data topic
        #     producer.produce(CRAWLED_DATA_TOPIC, json.dumps(message).encode('utf-8'), callback=delivery_report)
        #     print(f"Data sent to CONSUMER 2: {message}")
        #     producer.flush()
        #     return  # Exit on success
    except Exception as e:
        print(f"Attempt {retry_count + 1}: Failed to fetch {url}. Error: {e}")
        if retry_count < MAX_RETRIES - 1:
            # Republish message with incremented retry_count
            republish_message(url, retry_count + 1)
        else:
            # Publish error message after exhausting retries
            remarks = f"Failed to fetch {url} after {MAX_RETRIES} retries: {e}"
            error_message = {
                "type": "error",
                "data": {
                    "product_url": url,
                    "remarks": remarks,
                }
            }
            producer.produce(CRAWLED_DATA_TOPIC, json.dumps(error_message).encode('utf-8'), callback=delivery_report)
            print(f"Retry sent to CONSUMER 1 AGAIN: {error_message}")
            producer.flush()

def republish_message(url, retry_count):
    """
        > This function will resend the failed url to crawl to the first consumer.
        > retry_count will track the no of times the crawler run for the failed url till success
        > If the url still failed till the max_retires then the url will be send to send consumer to save to db in error_url tables
    """

    retry_message = {
        "url": url,
        "retry_count": retry_count
    }
    print(f"Republishing message: {retry_message}")
    producer.produce(KAFKA_URL_TOPIC, json.dumps(retry_message).encode('utf-8'))
    producer.flush()

def consume_messages():
    consumer.subscribe([KAFKA_URL_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())

            data = json.loads(msg.value().decode('utf-8'))
            url = data.get('url')
            retry_count = data.get('retry_count', 0)  # Default to 0 if not present
            print(f"Consumed message: {data}")
            crawl_url(url, retry_count)
    finally:
        consumer.close()

if __name__ == '__main__':
    print("Consumer is now listening for messages on the topic:", {KAFKA_URL_TOPIC})
    consume_messages()