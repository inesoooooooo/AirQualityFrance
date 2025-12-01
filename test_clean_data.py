import pandas as pd
from clean_data import AirQualityDataset

def test_clean_all_csv(tmp_path):
    # Création des dossiers temporaires
    raw = tmp_path / "raw"
    clean = tmp_path / "clean"
    raw.mkdir()
    clean.mkdir()

    # Création d'un CSV de test
    df_raw = pd.DataFrame({
        "Date de début": ["2020-05-01", "2019-01-01", None],
        "Polluant": ["NO2", "PM10", "O3"],
        "valeur": [12, None, 42],
        "Latitude": [48.85, 48.80, None],
        "Longitude": [2.35, None, 2.40],
        "nom site": ["Site A", "Site B", "Site C"],
        "Zas": ["Zone1", "Zone2", "Zone3"]
    })
    csv_file = raw / "test.csv"
    df_raw.to_csv(csv_file, sep=';', index=False)

    # Exécution du nettoyage
    dataset = AirQualityDataset(raw_folder=raw, clean_folder=clean)
    dataset.clean_all_csv()

    # Vérification du fichier clean créé
    clean_file = clean / "test_clean.csv"
    assert clean_file.exists()

    # Vérification du contenu
    df_clean = pd.read_csv(clean_file)
    expected_cols = ["Polluant", "valeur", "Latitude", "Longitude",
                     "nom site", "Zas", "Année"]
    assert list(df_clean.columns) == expected_cols
    assert len(df_clean) == 1
    assert df_clean.iloc[0]["Année"] == 2020

