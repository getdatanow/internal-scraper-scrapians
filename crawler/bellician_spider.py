import scrapy
import json

class BellicianSpider(scrapy.Spider):
    name = "bellician"
    allowed_domains = ["bellician.com"]
    
    
    def __init__(self, url=None, output_file=None, *args, **kwargs):
        super(BellicianSpider, self).__init__(*args, **kwargs)
        self.url = url
        self.output_file = output_file
        # print(f"Starting to crawl {self.url}")

    def start_requests(self):
        yield scrapy.Request(self.url,callback=self.parse, errback=self.error_back)

    def parse(self, response):
        dat=json.loads(response.xpath('//script[contains(@type,"application/ld+json") and contains(text(),"sku")]/text()').get())
        result_data = {
            'title':dat['name'],
            'price':str(dat['offers'][0]['price']),
            'image_url':dat['image'],
            'product_url':response.url,
            'description':dat['description'],
            'sku':dat['sku']
        }
        print(f'result for URL: {self.url}::{result_data}')
        yield result_data

    def error_back(self, failure):
        print(f"Error: {failure}")

# Configure logging
# configure_logging({"LOG_FORMAT": "%(levelname)s: %(message)s"})


if __name__ == "__main__":
    product_url = "https://www.bellician.com/products/586c122b5772ec17a0627107"
    b = BellicianSpider(product_url)
    
