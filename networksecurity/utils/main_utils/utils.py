from networksecurity.exception.exception import NetworkSecurityException
import sys
import yaml
import os
import numpy as np
from networksecurity.logging.logger import logging
import pickle

def read_yaml_file(file_path:str) -> dict:
    try:
        with open(file_path, "rb") as yaml_file:
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    try:
        
        if replace:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as file:
            yaml.dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)

def save_numpy_array_data(file_path: str, array: np.array):
    try:
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)

        with open(file_path, "wb") as file_obj: # wb = word binary
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys)
    

def save_object(file_path:str, obj: object):
    try:
        logging.info("Entered the save_object method")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as file_obj:
            pickle.dump(obj, file_obj)

        logging.info("Exite from save_object")

    except Exception as e:
        raise NetworkSecurityException(e, sys)

def load_object(file_path: str,) -> object:
    with open(file_path, "rb") as file_obj:
        print(file_obj)

        return pickle.load(file_obj)


def load_numpy_array_data(file_path: str) -> np.array:
    with open(file_path, "rb") as file_obj:
        return np.load(file_obj)
