import os
import sys
import json
from dotenv import load_dotenv
import certifi
import pandas as pd
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


load_dotenv()

ca = certifi.where()

MONGO_DB_URI = os.getenv("MONGO_DB_URI")

class NetworkDataExtract():
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def csv_to_json(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def insert_data(self, records, database, collection):
        try:
            self.database = database
            self.collection = collection
            self.records = records

            self.mongo_client = MongoClient(MONGO_DB_URI, server_api=ServerApi('1'))
            self.database = self.mongo_client[self.database]
            self.collection = self.database[self.collection]
            self.collection.insert_many(self.records)

            logging.info("Successfully pushed database to mongodb")

            return(len(self.records))

        except Exception as e:
            raise NetworkSecurityException(e,sys) 

if __name__ == '__main__':
    FILE_PATH = r"Network_Data\phisingData.csv"
    DATABASE= "CyberSense"
    Collection = "NetworkData"
    networkobj = NetworkDataExtract()
    records = networkobj.csv_to_json(file_path=FILE_PATH)
    no_of_records = networkobj.insert_data(records, DATABASE, Collection)
    print(no_of_records)