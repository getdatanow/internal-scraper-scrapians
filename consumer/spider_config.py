import sys
from pathlib import Path
import multiprocessing
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from crawler import bellician_spider
import encryption


import base64

def generate_filename_from_url(url):
    # Encode the URL to bytes and then Base64 encode it
    base64_encoded = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8')
    
    # Return the Base64-encoded string (without trailing '=' characters)
    return base64_encoded.rstrip("=")

def worker(url_queue):
    while not url_queue.empty():
        url = url_queue.get()

        output_folder = 'output'
        os.makedirs(output_folder, exist_ok=True)

        output_file = encryption.generate_filename_from_url(url)
        output_path = os.path.join(output_folder, f"{output_file}.json")

         # Set up the settings for the crawler
        settings = get_project_settings()
        settings.set('FEEDS', {
            output_path: {
                'format': 'json',
                'overwrite': True,
            },
        })
        # Disable or reduce log output
        settings.set('LOG_LEVEL', 'CRITICAL')
        
        process = CrawlerProcess(settings)
        process.crawl(bellician_spider.BellicianSpider, url=url)
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