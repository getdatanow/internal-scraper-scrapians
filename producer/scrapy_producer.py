from scrapy.crawler import CrawlerProcess
from pathlib import Path
import sys
from scrapy.utils.log import configure_logging
import logging

# Set up logging
configure_logging()
logging.basicConfig(level=logging.INFO)

sys.path.append(str(Path(__file__).parent.parent))

# Update the spider as needed
from crawler import BellicianUrlsSpider, SweetcareUrlsSpider


# Function to start the crawler
def start_crawl():
    """Run the spider and return the scraped data."""
    try:
        print("Starting the discovery spider...")

        # Create a CrawlerProcess instance
        process = CrawlerProcess()

        # Run the crawler
        process.crawl(SweetcareUrlsSpider.SweetcareUrlsSpider)
        process.start() 

    except ModuleNotFoundError as e:
        logging.error(f"Module Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Example usage
if __name__ == "__main__":
    start_crawl()
