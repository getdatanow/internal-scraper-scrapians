import logging
import sys
from pathlib import Path
import csv
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

sys.path.append(str(Path(__file__).parent.parent))
from utility.notification import send_slack_alert
from utility.save_data import save_to_db

class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter["url"] in self.ids_seen:
            raise DropItem(f"Item ID already seen: {adapter['url']}")
        else:
            self.ids_seen.add(adapter["url"])
            return item
        

class DiscoveryProcessingPipeline:
    """
    Handles the case for discovery to save the URLs in a CSV file.
    """
    def open_spider(self, spider):
        """Open CSV file and write header when the spider starts."""
        filename = f"output_{spider.name}.csv"
        self.file = open(filename, 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Index', 'URL'])
        self.index = 1

    def process_item(self, item, spider):
        """Write each URL to the CSV file immediately upon receiving it."""
        try:
            url = item.get('url') or item.get('product_url')
            if url:
                self.writer.writerow([self.index, url])
                self.index += 1
                self.file.flush()
                logging.info(f"URL saved: {url}")
            else:
                logging.warning("Received an item without a URL.")
        except Exception as e:
            logging.error(f"Error writing to CSV: {e}")
        
        return item

    def close_spider(self, spider):
        """Close the CSV file when the spider finishes."""
        self.file.close()


class DataProcessingPipeline:
    def process_item(self, item, spider):
        logging.debug(f"Processing item in DataProcessingPipeline...")
        # if not item or (len(item) == 1 and 'url' in item):
        #     logging.warning("No data received for item.")
        #     logging.debug("No data received for this item.")

        #     alert_msg = f"No data received for this item for url: {item.get('url')}"
        #     try:
        #         send_slack_alert(alert_msg)
        #         logging.info(f"Alert sent with message: {alert_msg}")
        #     except Exception as e:
        #         logging.debug(f"Failed to send ALERT: {e}")
            
        #     return None

        if "exception" in item:
            logging.error(f"Error in parsing: {item["exception"]}")
            alert_msg = f"Error in parsing: {item["exception"]} \n URL: {item["url"]}"
            try:
                """send alert and save to db for failure"""
                save_to_db(item, status="failure")
                print(f"Data is saved for failure URL: {item["url"]}")
                send_slack_alert(alert_msg)
            except Exception as e:
                logging.debug(f"Failed to send ALERT: {e}")
        else:
            try:
                """save data to db for success"""        
                if item:
                    logging.info(f"Data send for saving: {item}")
                    print(f"Data send for saving: {item}")
                    save_to_db(item, status="success")
                    print(f"Data is saved for success URL: {item["product_url"]}")
                else:
                    logging.info(f"No data to save in db")
            except Exception as e:
                logging.error(f"Error saving data: {e} ")

            # try:
            #     """save data to csv file"""
            #     self.writer.writerow([self.index, item['url']])
            #     self.index += 1
            #     self.file.flush()
            #     return item
            # except Exception as e:
            #     logging.error(f"Failed to save in json: {e}")
