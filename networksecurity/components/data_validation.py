from networksecurity.entity.artifact_entity import DataIngestionArtifact, DataValidationArtifact
from networksecurity.entity.config_entity import DataValidationConfig
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.utils.main_utils.utils import read_yaml_file
from networksecurity.utils.main_utils.utils import write_yaml_file
from networksecurity.logging.logger import logging
import pandas as pd
import sys
from scipy.stats import ks_2samp
import os


class DataValidation:
    def __init__(self, 
                 data_ingestion_artifact:DataIngestionArtifact, 
                 data_validation_config:DataValidationConfig):
        
        try:
            self.data_ingestion_artifact = data_ingestion_artifact
            self.data_validation_config = data_validation_config
            self._schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def validate_number_of_columns(self, dataframe:pd.DataFrame) -> bool:
        try:
            number_of_columns = len(self._schema_config)
            logging.info(f"Required number of columns : {number_of_columns}")
            logging.info(f"Data frame as columns: {len(dataframe.columns)}")
            
            if len(dataframe.columns) == number_of_columns:
                return True
            return False

        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def detect_dataset_drift(self, base_df, current_df, threshold=0.05) -> bool:
        try:

            status = True
            report={}
            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]

                is_same_dist = ks_2samp(d1, d2)

                if threshold <= is_same_dist.pvalue:
                    is_found = False 
                else:
                    is_found = True
                    status = False

                report.update({column:{
                    "p_value" : float(is_same_dist.pvalue),
                    "drift_status" : is_found
                }})
            
            drift_report_file_path = self.data_validation_config.drift_report_file_path

            #create dir
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)
            write_yaml_file(file_path=drift_report_file_path, content=report)
            logging.info(f"Data drift report saved at: {drift_report_file_path}")

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)
    
    def initiate_data_validation(self) -> DataIngestionArtifact:
        try:
            train_file_path = self.data_ingestion_artifact.trained_file_path
            test_file_path = self.data_ingestion_artifact.test_file_path

            # read the data from train and test

            train_data_frame = DataValidation.read_data(train_file_path)
            test_data_frame = DataValidation.read_data(test_file_path)

            # Validate number of columns

            status = self.validate_number_of_columns(dataframe=train_data_frame)

            if not status:
                error_message = "Train dataframe does not contain all columns.\n"
            
            status = self.validate_number_of_columns(dataframe=test_data_frame)

            if not status:
                error_message = "Test dataframe does not contain all columns.\n"

            ## Datadrift
            status = self.detect_dataset_drift(base_df=train_data_frame, current_df=test_data_frame)

            dir_path = os.path.dirname(self.data_validation_config.valid_train_file_path)
            os.makedirs(dir_path, exist_ok=True)

            train_data_frame.to_csv(
                self.data_validation_config.valid_train_file_path, index=False, header=True
            )

            test_data_frame.to_csv(
                self.data_validation_config.valid_test_file_path, index=False, header=True
            )
            

        except Exception as e:
            raise NetworkSecurityException(e, sys)