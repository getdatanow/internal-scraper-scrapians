import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.reactor import install_reactor
from twisted.internet import reactor
import json
from confluent_kafka import Producer
from config import KAFKA_BROKER, KAFKA_URL_TOPIC, delivery_report
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))

from crawler import BellicianUrlsSpider

# Install AsyncioSelectorReactor
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

# Create a CrawlerRunner instance
runner = CrawlerRunner()

# Function to start the crawler
def start_crawl():
    """Run the spider with the given URL and return the scraped data."""
    d = runner.crawl(BellicianUrlsSpider.BellicianUrlsSpider)
    d.addBoth(lambda _: reactor.stop())
    reactor.run()  # Blocks until the crawling is finished

# Example usage
if __name__ == "__main__":
    result_data = start_crawl()