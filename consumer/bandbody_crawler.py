import scrapy
import json
class BathandbodySpiderSpider(scrapy.Spider):
    name = "bathandbody"
    allowed_domains = ["bathandbodyworks.com"]
    start_urls = ["https://www.bathandbodyworks.com/p/twisted-peppermint-gentle-and-clean-foaming-hand-soap-028005848.html"]
    headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Referer": "https://www.bathandbodyworks.com/",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i"
        }
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url,callback=self.parse,headers=self.headers)
    def parse(self, response):
        dat=json.loads(response.xpath('//script[contains(@type,"text/javascript") and contains(text(),"product") and contains(text(),"pageInfo")]/text()').get().strip().replace('window.digitalData = ','').replace('};','}'))
        yield {
            'product_name':dat['product'][0]['productInfo']['productName'],
            'product_price':dat['product'][0]['price'],
            'product_image':dat['product'][0]['productInfo']['productImage'],
            'product_url':response.url,
            'description':dat['product'][0]['productInfo']['description'].replace('<p>','').replace('</p>',''),
            # 'sku':dat['sku']
        }