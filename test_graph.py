import pandas as pd
import pytest
from graph import charger_combiner_csv, filtrer_agreger, creer_graphique, map_villes

def test_filtrer_et_agreger():
    data = {
        'Annee': [2020, 2020, 2021, 2021],
        'Polluant': ['PM10', 'NO2', 'PM10', 'NO2'],
        'Zas': ['ZAG PARIS', 'ZAG PARIS', 'ZAG PARIS', 'ZAG PARIS'],
        'Concentration': [20, 30, 25, 35]
    }
    df = pd.DataFrame(data)
    df_final = filtrer_agreger(df, map_villes)

    # Vérifier les colonnes, nom de la ville et calcul de la moyenne
    assert all(col in df_final.columns for col in ['Annee', 'Polluant', 'Ville', 'Concentration'])
    assert df_final['Ville'].iloc[0] == 'Paris'
    assert df_final[df_final['Annee']==2020]['Concentration'].sum() == 50

def test_creer_graphique():
    data = {
        'Annee': [2020, 2020],
        'Polluant': ['PM10', 'NO2'],
        'Ville': ['Paris', 'Paris'],
        'Concentration': [20, 30]
    }
    df_final = pd.DataFrame(data)
    fig = creer_graphique(df_final)
    assert len(fig.data) == 2
    assert fig.layout.title.text.startswith("Évolution des concentrations")

