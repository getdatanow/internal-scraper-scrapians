import scrapy
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))


class BellicianSpider(scrapy.Spider):
    name = "bellician"
    allowed_domains = ["bellician.com"]
    
    custom_settings = {    
        'ITEM_PIPELINES': {
            'crawler.pipelines.DataProcessingPipeline': 300,
        },
    }
    
    def __init__(self, url=None, *args, **kwargs):
        super(BellicianSpider, self).__init__(*args, **kwargs)
        self.url = url
        print("Inside spider: stared crawling for URL: ", self.url)

    def start_requests(self):
        yield scrapy.Request(self.url,callback=self.parse, errback=self.error_back)

    def parse(self, response):
        dat=json.loads(response.xpath('//script[contains(@type,"application/ld+json") and contains(text(),"sku")]/text()').get())
        crawl_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        result_data = {
            'source_name':'bellician',
            'title':dat['name'],
            'price':str(dat['offers'][0]['price']),
            'image_url':dat['image'],
            'product_url':response.url,
            'description':dat['description'],
            'sku':dat['sku'],
            'crawled_date':crawl_date,
        }
        yield result_data

    def error_back(self, failure):
        print(f"Error: {failure}")

# Configure logging
# configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})


if __name__ == "__main__":
    product_url = "https://www.bellician.com/products/586c122b5772ec17a0627107"
    b = BellicianSpider(product_url)
    