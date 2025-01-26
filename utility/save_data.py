from dotenv import load_dotenv
import os
from pymongo import MongoClient
import logging

load_dotenv()
connection_string = "mongodb+srv://jyabadb:fakepass@cluster0.csfrd.mongodb.net/"
try:
    client = MongoClient(connection_string)
    print("Successful connection to MongoDB")
    
    # Check if the database exists
    db = client["getyourdatanow"]
    print("Database accessed successfully")
    
    # Check if the collection exists
    collection = db["ecommerce_test_new"]
    print("Collection accessed successfully")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

def save_to_db(data, status):
    """
        get the data from the pipeline and save to the mongodb
    """
    if status == "failure":
        """
        handle the failure status to save data to db in error collection
        """
        collection = db["error_status"]
        
    # Insert into MongoDB
    logging.info(f"Trying to save data to monogodb. Data: {data}")
    try:
        if isinstance(data, list):  # If data is a list of documents
            if data:
                collection.insert_many(data)
                logging.info(f"Inserted {len(data)} documents successfully.")
            else:
                logging.info("No data to insert.")
        elif isinstance(data, dict):  # If data is a single document
            print("Data is a dict")
            collection.insert_one(data)
            print("Inserted one document successfully.")
            logging.info("Inserted one document successfully.")
        else:
            print("Invalid data format. Expected dict or list of dicts.")
            logging.error("Invalid data format. Expected dict or list of dicts.")
    except Exception as e:
        logging.info(f"Error saving data to MongoDB: {e}")
        print(f"Error saving data to MongoDB: {e}")

# data = {
#     "url": "https://www.sweetcare.com/product123",
#     "name": "SweetCare Moisturizing Cream",
#     "sku": "SC123456",
#     "image": "https://www.sweetcare.com/images/product123.jpg",
#     "brand": {"name": "SweetCare"},
#     "description": "A hydrating cream for soft and glowing skin.",
#     "offers": {
#         "priceCurrency": "USD",
#         "itemCondition": "New",
#         "availability": "InStock",
#         "price": 29.99
#     }
# }

# try:
#     print("start to save to db")
#     save_to_db(data)
# except Exception as e:
#     print(f"Error: {e}")