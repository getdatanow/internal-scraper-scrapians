import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from utility.notification import send_slack_alert
from utility.save_data import save_to_db

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

        
