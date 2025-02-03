from scrapy.crawler import CrawlerProcess
from pathlib import Path
import sys
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
import logging

# Set up logging
configure_logging()
logging.basicConfig(level=logging.INFO)

sys.path.append(str(Path(__file__).parent.parent))

# Update the spider as needed
from crawler import BellicianUrlsSpider, SweetcareUrlsSpider, asos_urls


# Function to start the crawler
def start_crawl():
    """Run the spider and return the scraped data."""
    try:
        print("Starting the discovery spider...")

        settings = get_project_settings()
        settings.set('ITEM_PIPELINES', {
            'settings.pipelines.ErrorHandlingPipeline': 300,
        })

        # Disable or reduce log output
        settings.set('LOG_LEVEL', 'ERROR')


        # Create a CrawlerProcess instance
        process = CrawlerProcess(settings)

        # Run the crawler
        process.crawl(asos_urls.AsosUrlsSpider)
        process.start() 

    except ModuleNotFoundError as e:
        logging.error(f"Module Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# Example usage
if __name__ == "__main__":
    start_crawl()
