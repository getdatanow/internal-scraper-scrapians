import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.utils.reactor import install_reactor
from twisted.internet import reactor
import json
from confluent_kafka import Producer
from config import KAFKA_BROKER, KAFKA_URL_TOPIC, delivery_report
from pathlib import Path
import sys
from scrapy.utils.log import configure_logging
import logging

# Set up logging
configure_logging()
logging.basicConfig(level=logging.INFO)

sys.path.append(str(Path(__file__).parent.parent))

# update the spider as needed
from crawler import SweetcareUrlsSpider

# Install AsyncioSelectorReactor
install_reactor("twisted.internet.asyncioreactor.AsyncioSelectorReactor")

# Create a CrawlerRunner instance
runner = CrawlerRunner()

# Function to start the crawler
def start_crawl():
    """Run the spider with the given URL and return the scraped data."""
    try:
        print("Trying to run the discovery spider")
        # update the spider as needed
        d = runner.crawl(SweetcareUrlsSpider.SweetcareUrlsSpider)
        
        # Add error handling
        def handle_error(failure):
            logging.error(f"Spider failed with error: {failure}")
            if reactor.running:
                reactor.stop()
        
        d.addErrback(handle_error)  # Catch errors during the crawl
        d.addBoth(lambda _: reactor.stop())

        if not reactor.running:
            reactor.run()  # Blocks until the crawling is finished
    except ModuleNotFoundError as e:
        logging.error(f"Module Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Example usage
if __name__ == "__main__":
    result_data = start_crawl()