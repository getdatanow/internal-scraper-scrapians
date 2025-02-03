import scrapy
import json

class BellicianUrlsSpider(scrapy.Spider):
    name = "bellician_urls"
    allowed_domains = ["bellician.com"]
    start_urls = ["https://bellician.com"]

    custom_settings = {
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 429, 403],
        'RETRY_ENABLED': True,
        'ITEM_PIPELINES': {
            "crawler.pipelines.DuplicatesPipeline": 300,
            'crawler.pipelines.DiscoveryProcessingPipeline': 300,
        },
        'ROBOTSTXT_OBEY': False
    }

    headers = {
        'Host': 'www.bellician.com',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.bellician.com/products/BEAUTY',
        'Content-Type': 'application/json',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Priority': 'u=4',
        # Requests doesn't support trailers
        # 'Te': 'trailers',
    }

    def start_requests(self):
        yield scrapy.Request("https://bellician.com",callback=self.parse)

    def parse(self, response):
        ff=json.loads(response.xpath('//script[contains(@id,"__NEXT_DATA__")]/text()').get())['props']['context']['settings']['menu']
        urls=[]
        fff=ff
        for r in fff:
            url='/'+r['name']+'/'
            urls.append(url)
            if 'subs' in r:
                for ffff in r['subs']:
                    ur=url
                    ur+=ffff['name']
                    urls.append(ur)
                    if 'subs' in ffff:
                        for fffff in ffff['subs']:
                            u=ur
                            u+='/'+fffff['name']
                            urls.append(u)
        for url in urls:
            self.headers['Referer']='https://www.bellician.com/products'+url
            yield scrapy.Request('https://www.bellician.com/v3/products'+url,callback=self.parse_products,headers=self.headers,meta={"handle_httpstatus_list": [304,308]},dont_filter=True)

    def parse_products(self,response):
        for f in response.json():
            for u in f['options']:
                yield {
                    'url':'https://www.bellician.com/products/'+u['_id']
                }