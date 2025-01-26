import scrapy
import re
import json
import logging
from html import unescape
from datetime import datetime

class SweetcareSpider(scrapy.Spider):
    name = "sweetcare_product_spider"

    def __init__(self, url=None, *args, **kwargs):
        super(SweetcareSpider, self).__init__(*args, **kwargs)
        self.url = url
        print("Inside spider: stared crawling for URL: ", self.url)
    
    def clean_text(self, text):
        if not text:
            return ""
        try:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', text)

            # Unescape HTML entities
            text = unescape(text)

            # Remove line breaks and excess whitespace
            text = re.sub(r'\\[nrt"]', ' ', text)
            clean_text = re.sub(r'[\n\r]+', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text)
            clean_text = re.sub(r'\\+', '', clean_text)
            
            return clean_text.strip()
        except Exception as e:
            logging.error(f"Error cleaning text: {e}")
            return ""

    def start_requests(self):
        print(f"started request for {self.url}") 
        logging.info(f"started request for {self.url}")
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        print("Inside parse!!")
        try:
            parsed_data = response.xpath('//script[@type="application/ld+json"]//text()').get()

            if not parsed_data:
                print(f"No parsed data found for URL: {response.url}")
                return

            match = re.sub(r'[\n\r\t]', '', parsed_data)
        
            json_data = json.loads(match)

            result = {
                "source_name": 'sweetcare',
                "product_url": json_data.get('url', ''),
                "name": json_data.get('name', ''),
                "sku": json_data.get('sku', ''),
                "image": json_data.get('image', ''),
                "brand": json_data.get('brand', {}).get('name', ''),
                "description": self.clean_text(json_data.get('description', '')),
                "priceCurrency": json_data.get('offers', {}).get('priceCurrency', ''),
                "itemCondition": json_data.get('offers', {}).get('itemCondition', ''),
                "availability": json_data.get('offers', {}).get('availability', ''),
                "price": json_data.get('offers', {}).get('price', ''),
                "crawled_date": datetime.now()
            }

            print(f"result obtained for url: {result}")
        except Exception as e:
            exception = f"Unexpected error in spider: {e}"
            logging.info(f"Exception sent to the pipeline: {e}")
            
            result = {
                "url":self.url,
                "exception": exception
            }

        yield result
        
        

       