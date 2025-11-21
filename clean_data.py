import pandas as pd
import numpy as np
import os

class AirQualityDataset:
    def __init__(self, raw_folder="data/raw/", clean_folder="data/clean/"):
        self.raw_folder = raw_folder
        self.clean_folder = clean_folder
        os.makedirs(self.clean_folder, exist_ok=True)    


    def clean_all_csv(self):
        for filename in os.listdir(self.raw_folder):
            if filename.endswith(".csv"):
                path = os.path.join(self.raw_folder, filename)
                df = pd.read_csv(path, sep=';') 
                
                cols_keep = [
                    'Date de début', 'Polluant', 'valeur', 
                    'Latitude', 'Longitude', 'nom site', 'Zas'
                ]
                df = df[cols_keep]
                
                df = df.dropna(subset=['valeur', 'Latitude', 'Longitude'])
                
                df['Année'] = pd.to_datetime(df['Date de début'], errors='coerce').dt.year
                df = df.drop(columns=['Date de début'])
                df = df.dropna(subset=['Année'])
                
                clean_filename = filename.replace(".csv", "_clean.csv")
                clean_path = os.path.join(self.clean_folder, clean_filename)

                df.to_csv(clean_path, index=False)
                print(f"{clean_filename} enregistré dans clean/")
if __name__ == "__main__":
    dataset = AirQualityDataset()
    dataset.clean_all_csv()
