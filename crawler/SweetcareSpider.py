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
        url = response.url
        crawl_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        try:

            """Parse product pages."""
            dat = response.xpath('//script[@type="application/ld+json"]//text()').get()
            if not dat:
                logging.error(f"No JSON-LD data found for URL: {url}")
                return

            try:
                match = re.sub(r'[\n\r\t]', '', dat)
                dat = json.loads(match)
            except json.JSONDecodeError as e:
                logging.error(f"JSON parsing error for URL: {url}, Error: {str(e)}")
                return
            
            data_source = dat[0] if isinstance(dat, list) and len(dat) > 0 else dat
            try:
                product_name = data_source.get('name', None)
                priceCurrency = data_source.get('offers', {}).get('priceCurrency', None) if isinstance(data_source, dict) else None
                product_price = data_source.get('offers', {}).get('price', None) if isinstance(data_source, dict) else None
                product_image = data_source.get('image', None)
                brand = data_source.get('brand', {}).get('name', None)
                itemCondition = data_source.get('offers', {}).get('itemCondition', None) if isinstance(data_source, dict) else None
                description = (
                    self.clean_text(data_source[0].get('description', '')) if isinstance(data_source, list) and len(data_source) > 0 and isinstance(data_source[0], dict)
                    else self.clean_text(data_source.get('description', ''))
                )
                sku = data_source.get('sku', None)
                availability = data_source.get('offers', {}).get('availability', None) if isinstance(data_source, dict) else None
            except (KeyError, TypeError):
                product_name = None
                priceCurrency = None
                product_price = None
                product_image = None
                description = None
                sku = None
                brand = None
                itemCondition = None
                availability = None

            all_details = {
                'crawl_date': crawl_date,
                "source_name": "sweetcare",
                'product_url': url,
                'product_name': product_name,
                'price_currency': priceCurrency,
                'product_price': product_price,
                'brand': brand,
                'itemCondition': itemCondition,
                'availability': availability,
                'product_image': product_image,
                'description': description,
                'sku': sku
            }
            yield all_details
        except Exception as e:
            exception = f"Unexpected error in spider: {e}"
            logging.info(f"Exception sent to the pipeline: {e}")
            
            result = {
                "url":self.url,
                "exception": exception
            }
            
            yield result