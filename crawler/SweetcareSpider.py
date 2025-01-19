import scrapy
import re
import json
from lxml import html
from lxml.etree import ParserError
import logging
from html import unescape




class SweetcareSpider(scrapy.Spider):
    name = "sweetcare_product_spider"
    # base_url ="https://www.perfumesclub.us/"
    start_urls = "https://www.sweetcare.com/ru/crescina-transdermic-hfsc-complete-treatment-vials-women-p-015292ce?st=03"




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

    def __init__(self, url=None, output_file=None, *args, **kwargs):
        super(SweetcareSpider, self).__init__(*args, **kwargs)
        self.url = url
        self.output_file = output_file
        print("Inside spider: stared crawling for URL: ", self.url)

    def start_requests(self):
        print(f"started parsing for {self.url}")
        yield scrapy.Request(url=self.start_urls, callback=self.parse)

    def parse(self, response):
        print('inside parser')
        parsed_data = response.xpath('//script[@type="application/ld+json"]//text()').get()

        match = re.sub(r'[\n\r\t]', '', parsed_data)
        json_data = json.loads(match)

        result =  {
            "url":json_data[0]['url'],
            "name" :json_data[0]['name'],
            "sku":json_data[0]['sku'],
            "image":json_data[0]['image'],
            "brand": json_data[0]['brand']['name'],
            "description" : self.clean_text(json_data[0]['description']),
            "priceCurrency" :json_data[0]['offers']['priceCurrency'],
            "itemCondition":json_data[0]['offers']['itemCondition'],
            "availability": json_data[0]['offers']['availability'],
            "price" : json_data[0]['offers']['price'],
        }

        print(f"this is the result: {result.urla}")
        yield(result)
        

       