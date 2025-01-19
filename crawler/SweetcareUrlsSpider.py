import scrapy
from parsel import Selector
from confluent_kafka import Producer
from config import KAFKA_BROKER, KAFKA_URL_TOPIC, delivery_report
import json

class SweetcareUrlsSpider(scrapy.Spider):
    name = "sweetcare_urls"
    allowed_domains = ["sweetcare.com"]
    start_urls = ["https://sweetcare.com"]

    custom_settings = {
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 429, 403],
        'RETRY_ENABLED': True,
        # 'DOWNLOADER_MIDDLEWARES': {
        #     "scrapy_crawlers.middlewares.SingleProxyMiddleware": 543,
        # },
        # 'PROXY_URL': "gw.ntnt.io:5959:jyabatech-res-US:B4Cq9fnpiMa1hMx",
        # 'ITEM_PIPELINES': {
        #     "scrapy_crawlers.pipelines.DuplicatesPipeline": 300,
        # },
        'ROBOTSTXT_OBEY': False
    }
    # Initialize Kafka producer
    producer = Producer({'bootstrap.servers': KAFKA_BROKER})

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Referer': 'https://www.sweetcare.com/np/cm/hair',
        'Content-Type': 'application/json; charset=utf-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        # 'Cookie': 'reloadmenu=0; navNPersistent=countryGroup=10&country=NP&lang=EN&currencyAbbr=NPR; ASP.NET_SessionId=pn4pk1h0lcv0t55pqlm23knt; nav=dn=&did=1&unuId=3b58158e-d67c-4e8b-b3c0-2bcfa44f2269&nsci=nsci; ww=1300; hd=0; __kla_id=eyJjaWQiOiJOakkyT1RSaFpqUXRZak16WWkwME4yWmxMV0UyTmpVdFlqaGtNR1U1WkRnNU5EZzQiLCIkcmVmZXJyZXIiOnsidHMiOjE3MzUxMjI0ODksInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd3d3LnN3ZWV0Y2FyZS5jb20vbnAifSwiJGxhc3RfcmVmZXJyZXIiOnsidHMiOjE3MzUxMjI2NjIsInZhbHVlIjoiIiwiZmlyc3RfcGFnZSI6Imh0dHBzOi8vd3d3LnN3ZWV0Y2FyZS5jb20vbnAifX0=; CookieConsent={stamp:%27yo5bic24Flot50yNGxK3uXAkK2gBaaZpRmEVZUiyH9jTK+/fcpn6Bg==%27%2Cnecessary:true%2Cpreferences:true%2Cstatistics:true%2Cmarketing:true%2Cmethod:%27explicit%27%2Cver:1%2Cutc:1735122493378%2Cregion:%27np%27}; _gcl_au=1.1.1214975893.1735122494; _ga=GA1.1.924413820.1735122489; _ga_PFQEGRV8LJ=GS1.1.1735122488.1.1.1735122742.39.1.2011459911; _fbp=fb.1.1735122494709.187164503996768363; _uetsid=f2ad0e40c2aa11efacba21cbaf8694b2; _uetvid=f2ad1dc0c2aa11ef8d67c727ebdfa99e',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=0',
        # Requests doesn't support trailers
        # 'TE': 'trailers',
    }

    def start_requests(self):
        print("started the spider")
        yield scrapy.Request("https://sweetcare.com",callback=self.parse)

    def parse(self, response):
        for url in response.xpath('//a[contains(@href,"/b") or contains(@href,"/c")]/@href').extract():
            self.headers['Referer']='https://www.sweetcare.com'+url
            yield scrapy.Request('https://www.sweetcare.com/ajax/listProductsH.ashx?a=loadMore&p=2&st=2',callback=self.parse_products_url,headers=self.headers,dont_filter=True,meta={'page':2,'ref':'https://www.sweetcare.com'+url})

    def parse_products_url(self,response):
        page=response.meta['page']+1
        for item in response.json():
            if 'productList' in item['key']:
                s=Selector(item['value'])
                try:
                    yield {
                        'url':'https://www.sweetcare.com'+s.xpath('//a/@href').get()
                    }
                    product_url = 'https://www.sweetcare.com'+s.xpath('//a/@href').get()

                    # Create message for Kafka
                    message = {
                        'url': product_url,
                        'retry_count': 0
                    }
                    print(f"Message sent: {message}")

                    # Send message to Kafka
                    self.producer.produce(
                        KAFKA_URL_TOPIC, 
                        json.dumps(message).encode('utf-8'), 
                        callback=delivery_report
                    )
                except:
                    pass
        self.headers['Referer']=response.meta['ref']
        if len(response.json())>4:
            yield scrapy.Request('https://www.sweetcare.com/ajax/listProductsH.ashx?a=loadMore&p='+str(page)+'&st=2',callback=self.parse_products_url,headers=self.headers,dont_filter=True,meta={'page':page,'ref':response.meta['ref']})