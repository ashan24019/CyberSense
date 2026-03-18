from networksecurity.constants.training_pipeline import SAVED_MODEL_DIR, MODEL_FILE_NAME
import os

class NetworkModel:
    def __init__(self, preprocessor, model):
        self.preprocessor = preprocessor
        self.model = model
    
    def predict(self, x):
        x_transform = self.preprocessor.transform(x)
        y_hat = self.model.predict(x_transform)

        return y_hat