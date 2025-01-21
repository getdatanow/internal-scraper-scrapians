import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utility.notification import send_slack_alert

class ErrorHandlingPipeline:
    def process_item(self, item, spider):
        logging.debug(f"Processing item in ErrorHandlingPipeline...")
        if not item or (len(item) == 1 and 'url' in item):
            logging.warning("No data received for item.")
            logging.debug("No data received for this item.")

            alert_msg = f"No data received for this item for url: {item.get('url')}"
            try:

                send_slack_alert(alert_msg)
                logging.info(f"Alert sent with message: {alert_msg}")
            except Exception as e:
                logging.debug(f"Failed to send ALERT: {e}")
            
            return None
            
        try:
            return item  
        except Exception as e:
            spider.crawler.stats.inc_value('pipeline/error_count')
            logging.error(f"Error processing item: {e}")
            alert_msg = f"Error processing item: {e}"
            try:
                send_slack_alert(alert_msg)
            except Exception as e:
                logging.debug(f"Failed to send ALERT: {e}")

            return None
