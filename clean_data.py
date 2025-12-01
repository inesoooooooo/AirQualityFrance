import pandas as pd
import numpy as np
import os

class AirQualityDataset:
    """
    Classe pour gérer le nettoyage des fichiers CSV bruts
    Attributs :
    raw_folder : str (chemin du dossier qui contient les fichiers CV bruts)
    clean_folder : str (chemin du dossier où se trouveront les fichiers nettoyés)
    """
    def __init__(self, raw_folder="data/", clean_folder="data/clean/"):
        """
        Initialise les chemins des dossiers et crée le dossier de fichiers nettoyés
        Paramètres :
        raw_folder : str, optionnel (par défaut "data/")
        clean_folder : str, optionnel (par défaut "data/clean/")
        """
        self.raw_folder = raw_folder
        self.clean_folder = clean_folder
        os.makedirs(self.clean_folder, exist_ok=True)    


    def clean_all_csv(self):
        """
        Étapes :
        1- Lire le CSV avec pandas
        2- Conserve uniquement certaines colonnes
        3- Supprimer les lignes avec des valeurs manquantes dans 'valeur', 'Lattitude', 'Longitude'
        4- Extraire l'année depuis la colonne 'Date de début' at ajouter une colonne 'Année'
        5- Sauvegarder le CSV nettoyé avce le suffixe "_clean"
        """
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


""" Test unitaire """

    df_test = pd.DataFrame({
        "Date de début": ["2023-01-01", None],
        "Polluant": ["PM10", "NO2"],
        "valeur": [10, None],
        "Latitude": [48.85, 48.85],
        "Longitude": [2.35, None],
        "nom site": ["site1", "site2"],
        "Zas": ["ZAG PARIS", "ZAG PARIS"]
    })

    # Simuler le nettoyage
    df_clean = df_test.dropna(subset=['valeur', 'Latitude', 'Longitude'])
    df_clean['Année'] = pd.to_datetime(df_clean['Date de début'], errors='coerce').dt.year
    df_clean = df_clean.drop(columns=['Date de début'])
    df_clean = df_clean.dropna(subset=['Année'])

    # Affiche True si OK
    print(len(df_clean) == 1 and "Année" in df_clean.columns)  
