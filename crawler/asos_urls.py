import scrapy
import re
from scrapy.utils.project import get_project_settings


class AsosUrlsSpider(scrapy.Spider):
    name = "asos_urls"
    allowed_domains = ["asos.com"]
    start_urls = ["https://asos.com"]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super().from_crawler(crawler, *args, **kwargs)
        pipelines = dict(crawler.settings.get('ITEM_PIPELINES', {}))
        pipelines['crawler.pipelines.DuplicatesPipeline'] = 400
        crawler.settings.set('ITEM_PIPELINES', pipelines)
        return spider
    
    custom_settings = {
        'RETRY_TIMES': 10,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 429, 403],
        'RETRY_ENABLED': True,
        'ROBOTSTXT_OBEY': False
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:133.0) Gecko/20100101 Firefox/133.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        # 'Accept-Encoding': 'gzip, deflate, br, zstd',
        'DNT': '1',
        'Sec-GPC': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Priority': 'u=0, i',
    }

    def start_requests(self):
        pipelines = self.crawler.settings.getdict('ITEM_PIPELINES')
        print(f"Registered Pipelines: {pipelines}")  # Debug output
        yield scrapy.Request('https://www.asos.com/product-sitemap-index-COM.xml',callback=self.parse,headers=self.headers)

    def parse(self, response):
        for url in re.findall(r"<loc>(.*?)</loc>", response.text):
            if 'product-sitemap' in url:
                yield scrapy.Request(url,callback=self.parse,headers=self.headers)
            else:
                yield {
                    'url':url
                }