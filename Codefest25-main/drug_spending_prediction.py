import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
import json
import logging
import matplotlib.pyplot as plt
import os

class DrugSpendingPredictor:
    def __init__(self):
        """Initialize the DrugSpendingPredictor."""
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('drug_predictor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.data = None
        self.models_total = {}
        self.models_avg = {}

    def load_local_data(self, file_path='drug_data.json'):
        """
        Load data from local JSON file.
        
        Args:
            file_path (str): Path to the JSON file
        """
        self.logger.info(f"Loading data from: {file_path}")
        
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                self.data = pd.DataFrame(json_data)
                self.logger.info(f"Successfully loaded {len(self.data)} records")
                return True
        except FileNotFoundError:
            self.logger.error(f"File not found: {file_path}")
            return False
        except json.JSONDecodeError:
            self.logger.error("Error decoding JSON file")
            return False
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            return False

    def preprocess_data(self):
        """Clean and prepare the data for analysis."""
        if self.data is None:
            self.logger.error("No data to preprocess")
            return False
            
        try:
            # Ensure only numeric columns are processed
            numeric_columns = [col for col in self.data.columns if col.startswith('Tot_Spndng_') or col.startswith('Avg_Spnd_Per_Bene_')]
            
            for col in numeric_columns:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            # Handle missing values (fill NaN with column means)
            self.data[numeric_columns] = self.data[numeric_columns].fillna(self.data[numeric_columns].mean())

            self.logger.info("Data preprocessing completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during preprocessing: {e}")
            return False


    def train_models(self):
        """Train prediction models for each unique drug."""
        if self.data is None:
            self.logger.error("No data available for training")
            return False

        years = np.array(range(2018, 2023)).reshape(-1, 1)
        success_count = 0
        
        for _, drug in self.data.iterrows():
            drug_name = drug['Brnd_Name']
            
            try:
                # Prepare spending data
                total_spending = np.array([float(drug[f'Tot_Spndng_{year}']) for year in range(2018, 2023)])
                avg_spending = np.array([float(drug[f'Avg_Spnd_Per_Bene_{year}']) for year in range(2018, 2023)])
                
                # Train models
                model_total = LinearRegression().fit(years, total_spending)
                model_avg = LinearRegression().fit(years, avg_spending)
                
                # Store models
                self.models_total[drug_name] = model_total
                self.models_avg[drug_name] = model_avg
                
                success_count += 1
                
            except Exception as e:
                self.logger.error(f"Error training models for {drug_name}: {e}")
                
        self.logger.info(f"Successfully trained models for {success_count} drugs")
        return success_count > 0

    def predict_future(self, years_ahead=3):
        """Make predictions for future years."""
        if not self.models_total:
            self.logger.error("No trained models available")
            return None

        future_years = np.array(range(2023, 2023 + years_ahead)).reshape(-1, 1)
        predictions = {}
        
        for drug_name in self.models_total.keys():
            try:
                total_predictions = self.models_total[drug_name].predict(future_years)
                avg_predictions = self.models_avg[drug_name].predict(future_years)
                
                print(f"\nPredictions for {drug_name}:")
                for i, year in enumerate(range(2023, 2023 + years_ahead)):
                    print(f"Year {year}:")
                    print(f"  Predicted Total Spending: ${total_predictions[i]:,.2f}")
                    print(f"  Predicted Avg Spending per Beneficiary: ${avg_predictions[i]:,.2f}")
                    
                predictions[drug_name] = {
                    'years': list(range(2023, 2023 + years_ahead)),
                    'total_spending': total_predictions,
                    'avg_spending': avg_predictions
                }
                
            except Exception as e:
                self.logger.error(f"Prediction error for {drug_name}: {e}")
                
        return predictions

def main():
    predictor = DrugSpendingPredictor()
    
    print("Loading data...")
    if predictor.load_local_data():
        print("Processing data...")
        if predictor.preprocess_data():
            print("Training models...")
            if predictor.train_models():
                print("\nMaking predictions...")
                predictor.predict_future(3)

if __name__ == "__main__":
    main()