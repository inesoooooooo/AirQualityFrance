import pandas as pd
import numpy as np
import pytest
from app import get_air_quality_index, load_clean_data, nettoyer_nom_ville

@pytest.mark.parametrize(
    "polluant,valeur,expected",
    [
        ("NO2", 20, "BON"),      
        ("NO2", 50, "MOYEN"),    
        ("NO2", 150, "DÉGRADÉ"),  
        ("NO2", 200, "MAUVAIS"),   
        ("PM10", 10, "BON"),     
        ("PM10", 30, "MOYEN"),     
        ("PM10", 60, "DÉGRADÉ"),  
        ("PM10", 100, "MAUVAIS"),   
        ("O3", 50, "NON CLASSIFIÉ")
    ]
)
def test_get_air_quality_index(polluant, valeur, expected):
    row = pd.Series({"polluant": polluant, "valeur": valeur})
    assert get_air_quality_index(row) == expected


def test_load_clean_data(tmp_path):
    df1 = pd.DataFrame({
        "polluant": ["NO2", "PM10"],
        "année": [2020, 2020],
        "latitude": [45.0, 46.0],
        "longitude": [3.0, 4.0],
        "valeur": [30, 50],
        "nom_site": ["site1", "site2"],
        "zas": ["ville1", "ville2"]
    })
    df1.to_csv(tmp_path / "test1_clean.csv", index=False)

    df_loaded = load_clean_data(folder=str(tmp_path))
    
    assert "indice_qualite_air" in df_loaded.columns
    assert df_loaded.shape[0] == 2

def test_load_clean_data_empty_folder(tmp_path):
    with pytest.raises(ValueError):
        load_clean_data(folder=str(tmp_path))


@pytest.mark.parametrize(
    "ville,expected",
    [
        ("Paris", "Paris"),
        ("Marseille Aix", "Marseille_Aix"),
        ("Nantes Saint-Lazaire", "Nantes_Saint_Lazaire"),
    ]
)
def test_nettoyer_nom_ville(ville, expected):
    assert nettoyer_nom_ville(ville) == expected
