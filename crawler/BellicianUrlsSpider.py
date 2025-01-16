import scrapy
import json
from confluent_kafka import Producer
from config import KAFKA_BROKER, KAFKA_URL_TOPIC, delivery_report


class BellicianUrlsSpider(scrapy.Spider):
    name = "bellician_urls"
    allowed_domains = ["bellician.com"]
    start_urls = ["https://bellician.com"]
    
    # Add message counter as class variable
    message_count = 0
    MAX_MESSAGES = 20

    custom_settings = {
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 429, 403],
        'RETRY_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
    }

    headers = {
        'Host': 'www.bellician.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Content-Type': 'application/json',
    }

    # Initialize Kafka producer
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})

    def start_requests(self):
        """Initial request to scrape the website."""
        yield scrapy.Request("https://bellician.com", callback=self.parse)

    def parse(self, response):
        """Extract menu URLs from the response."""
        menu_data = json.loads(response.xpath('//script[contains(@id,"__NEXT_DATA__")]/text()').get())['props']['context']['settings']['menu']
        urls = []
        for menu_item in menu_data:
            base_url = '/' + menu_item['name'] + '/'
            urls.append(base_url)
            if 'subs' in menu_item:
                for sub_menu in menu_item['subs']:
                    sub_url = base_url + sub_menu['name']
                    urls.append(sub_url)
                    if 'subs' in sub_menu:
                        for sub_sub_menu in sub_menu['subs']:
                            deep_url = sub_url + '/' + sub_sub_menu['name']
                            urls.append(deep_url)

        for url in urls:
            if self.message_count >= self.MAX_MESSAGES:
                self.log(f"Maximum message limit ({self.MAX_MESSAGES}) reached. Stopping spider.")
                return
            
            self.headers['Referer'] = 'https://www.bellician.com/products' + url
            yield scrapy.Request(
                'https://www.bellician.com/v3/products' + url,
                callback=self.parse_products,
                headers=self.headers,
                meta={"handle_httpstatus_list": [304, 308]},
                dont_filter=True
            )

    def parse_products(self, response):
        """Extract product URLs and send them to Kafka."""
        products = response.json()
        for product in products:
            if self.message_count >= self.MAX_MESSAGES:
                self.log(f"Maximum message limit ({self.MAX_MESSAGES}) reached. Stopping processing.")
                return
                
            for option in product.get('options', []):
                if self.message_count >= self.MAX_MESSAGES:
                    return
                    
                product_url = 'https://www.bellician.com/products/' + option['_id']
                
                # Create message for Kafka
                message = {
                    'url': product_url,
                    'retry_count': 0
                }

                # Send message to Kafka
                self.producer.produce(
                    KAFKA_URL_TOPIC, 
                    json.dumps(message).encode('utf-8'), 
                    callback=delivery_report
                )
                
                self.message_count += 1
                print(f"Sent to Kafka: {message} (Message {self.message_count} of {self.MAX_MESSAGES})")
                self.log(f"Sent to Kafka: {message} (Message {self.message_count} of {self.MAX_MESSAGES})")

    def close(self, reason):
        """Ensure all Kafka messages are sent before shutting down."""
        self.producer.flush()
        self.log(f"Kafka producer flushed. Total messages sent: {self.message_count}")
