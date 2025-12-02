import pandas as pd
import numpy as np
import pytest
# Ces fonctions sont importées depuis votre fichier app.py
from app import get_air_quality_index, load_clean_data, nettoyer_nom_ville


# -----------------------------------------------------------
# Test de la fonction get_air_quality_index
# -----------------------------------------------------------

@pytest.mark.parametrize(
    "polluant,valeur,expected",
    [
        # Tests NO2
        ("NO2", 20, "BON"),      # NO2 <= 40
        ("NO2", 50, "MOYEN"),     # 40 < NO2 <= 80
        ("NO2", 150, "DÉGRADÉ"),  # 80 < NO2 <= 180
        ("NO2", 200, "MAUVAIS"),   # NO2 > 180
        
        # Tests PM10
        ("PM10", 10, "BON"),      # PM10 <= 20
        ("PM10", 30, "MOYEN"),     # 20 < PM10 <= 40
        ("PM10", 60, "DÉGRADÉ"),  # 40 < PM10 <= 70
        ("PM10", 100, "MAUVAIS"),   # PM10 > 70
        
        # Test Non Classifié
        ("O3", 50, "NON CLASSIFIÉ")
    ]
)
def test_get_air_quality_index(polluant, valeur, expected):
    # Prépare une ligne de DataFrame pour simuler l'entrée de la fonction
    row = pd.Series({"polluant": polluant, "valeur": valeur})
    # Vérifie que le résultat de la fonction est égal au résultat attendu (expected)
    assert get_air_quality_index(row) == expected


# -----------------------------------------------------------
# Tests de la fonction load_clean_data
# -----------------------------------------------------------

# Test de chargement réussi
def test_load_clean_data(tmp_path):
    # Crée un dossier temporaire pour simuler le dossier 'data/clean/'
    
    # Prépare un petit DataFrame de test
    df1 = pd.DataFrame({
        "polluant": ["NO2", "PM10"],
        "année": [2020, 2020],
        "latitude": [45.0, 46.0],
        "longitude": [3.0, 4.0],
        "valeur": [30, 50],
        "nom_site": ["site1", "site2"],
        "zas": ["ville1", "ville2"]
    })
    # Sauvegarde le DataFrame dans le dossier temporaire avec le nom attendu (*_clean.csv)
    df1.to_csv(tmp_path / "test1_clean.csv", index=False)

    # Appelle la fonction de chargement en lui donnant le chemin temporaire
    df_loaded = load_clean_data(folder=str(tmp_path))
    
    # Assertions : Vérifie les propriétés du DataFrame chargé
    assert "indice_qualite_air" in df_loaded.columns
    assert df_loaded.shape[0] == 2

# Test de dossier vide
def test_load_clean_data_empty_folder(tmp_path):
    # Vérifie que la fonction lève bien l'erreur 'ValueError'
    # si le dossier ne contient aucun fichier *_clean.csv.
    with pytest.raises(ValueError):
        load_clean_data(folder=str(tmp_path))


# -----------------------------------------------------------
# Test de la fonction nettoyer_nom_ville
# -----------------------------------------------------------

@pytest.mark.parametrize(
    "ville,expected",
    [
        ("Paris", "Paris"),
        ("Marseille Aix", "Marseille_Aix"),
        ("Nantes Saint-Lazaire", "Nantes_Saint_Lazaire"),
        ("Nice-Côte d'Azur", "Nice_Côte_d'Azur"), # Test avec le tiret (hyphen)
        ("Toulon/Hyères", "Toulon_Hyères") # Test avec le slash
    ]
)
def test_nettoyer_nom_ville(ville, expected):
    # Vérifie que la ville est nettoyée comme prévu pour être utilisée dans un nom de fichier
    assert nettoyer_nom_ville(ville) == expected