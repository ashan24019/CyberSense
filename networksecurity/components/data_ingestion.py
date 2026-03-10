from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

## configuration of the Data Ingestion Config
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_DB_URI")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def export_collection_as_df(self):
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = MongoClient(MONGO_DB_URI, server_api=ServerApi('1'))

            collection = self.mongo_client[database_name][collection_name]

            df = pd.DataFrame(list(collection.find()))
            if "_id" in df.columns.to_list():
                df = df.drop(columns=["_id"])
            
            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def export_data_into_feature_store(self, dataframe : pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            #creating a folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)

            return dataframe
        
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size= self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Perform train test split on the dataframe.")
            
            dir_path = os.path.dirname(self.data_ingestion_config.testing_file_path)

            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train test file path.")

            train_set.to_csv(self.data_ingestion_config.training_file_path)
            test_set.to_csv(self.data_ingestion_config.testing_file_path)

        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    def initiate_data_ingestion(self):
        try:
            data_frame = self.export_collection_as_df()
            data_frame = self.export_data_into_feature_store(data_frame)
            self.split_data_as_train_test(data_frame)
            data_ingestion_artifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path, 
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            return data_ingestion_artifact
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
