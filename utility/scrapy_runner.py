import sys
from pathlib import Path
import multiprocessing
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import uuid
import re
from urllib.parse import urlparse

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from crawler import SweetcareSpider


def generate_file_name(url: str) -> str:
    """Generate a unique, readable filename from a product URL."""
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.split(':')[0].split('.')
        
        domain = domain_parts[-2] if len(domain_parts) > 2 else domain_parts[0]
        domain = re.sub(r'[^a-zA-Z0-9]', '_', domain)
        
        unique_id = uuid.uuid4().hex[:12]
        
        return f"{domain}_{unique_id}.json"
    
    except Exception as e:
        return f"Error in generating filename: {e}"

def worker(url_queue):
    while not url_queue.empty():
        url = url_queue.get()

        output_folder = 'output'
        os.makedirs(output_folder, exist_ok=True)

        output_file = generate_file_name(url)
        output_path = os.path.join(output_folder, f"{output_file}")

         # Set up the settings for the crawler
        settings = get_project_settings()
        settings.set('FEEDS', {
            output_path: {
                'format': 'json',
                'overwrite': True,
            },
        })

        settings.set('ITEM_PIPELINES', {
            'settings.pipelines.ErrorHandlingPipeline': 300,
        })
        
        # Disable or reduce log output
        settings.set('LOG_LEVEL', 'DEBUG')

        # Print registered pipelines
        print("Final Registered Pipelines:", settings.getdict('ITEM_PIPELINES'))

        process = CrawlerProcess(settings)
        process.crawl(SweetcareSpider.SweetcareSpider, url=url)
        process.start()

def run_multiprocessing(urls):
    url_queue = multiprocessing.Queue()

    # for url in urls:
    #     url_queue.put(url)

    url_queue.put(urls)

    processes = []
    num_workers = 2  # Use multiple workers (adjust as needed)
    
    # Create worker processes
    for _ in range(num_workers):
        p = multiprocessing.Process(target=worker, args=(url_queue,))
        processes.append(p)
        p.start()  # Start each worker process

    # Wait for all processes to finish
    for p in processes:
        p.join()