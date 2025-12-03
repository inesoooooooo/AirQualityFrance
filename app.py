import plotly.express as px
import pandas as pd
import os
import glob
import numpy as np


def get_air_quality_index(row):
    """
    Classifie une concentration de polluant (valeur en µg/m³) selon l'indice ATMO simplifié.
    Retourne une des 4 catégories : 'BON', 'MOYEN', 'DÉGRADÉ', 'MAUVAIS'.

    Les seuils sont basés sur l'indice ATMO Français pour les polluants NO2 et PM10.
    Toute autre polluant est classifié comme "NON CLASSIFIÉ".

    Args:
        row (pd.Series): Ligne de données contenant au moins 'polluant' (str) et 'valeur' (float).

    Returns:
        str: La catégorie de qualité de l'air ('BON', 'MOYEN', 'DÉGRADÉ', 'MAUVAIS', 'NON CLASSIFIÉ').
    """
    polluant = row['polluant']
    valeur = row['valeur']

    seuils = {
        "NO2": {
            "BON": 40,
            "MOYEN": 80,
            "DÉGRADÉ": 180,
            "MAUVAIS": np.inf
        },
        "PM10": {
            "BON": 20,
            "MOYEN": 40,
            "DÉGRADÉ": 70,
            "MAUVAIS": np.inf
        }
    }

    if polluant not in seuils:
        return "NON CLASSIFIÉ"

    seuil = seuils[polluant]
    
    if valeur <= seuil["BON"]:
        return "BON"
    elif valeur <= seuil["MOYEN"]:
        return "MOYEN"
    elif valeur <= seuil["DÉGRADÉ"]:
        return "DÉGRADÉ"
    else:
        return "MAUVAIS"


def load_clean_data(folder="data/clean/"):
    """
    Charge et nettoie les données du dossier data/clean

    Concatène tous les fichiers CSV se terminant par '_clean.csv' dans le dossier,
    standardise les noms de colonnes, convertit la colonne 'valeur' en numérique,
    supprime les lignes avec des valeurs manquantes essentielles (valeur, latitude,
    longitude) et ajoute la colonne 'indice_qualite_air' en utilisant get_air_quality_index.

    Args:
        folder (str): Le chemin du dossier contenant les fichiers CSV nettoyés.
                      Par défaut, "data/clean/".

    Returns:
        pd.DataFrame: Un DataFrame unique et nettoyé avec l'indice de qualité de l'air calculé.

    Raises:
        ValueError: Si aucun fichier *_clean.csv n'est trouvé dans le dossier spécifié.
    """
    all_files = glob.glob(os.path.join(folder, "*_clean.csv"))
    dfs = []

    for f in all_files:
        try:
            df = pd.read_csv(f, dtype={'polluant': str}) 
            dfs.append(df)
        except Exception as e:
            print(f"Erreur de lecture du fichier {f}: {e}")
            continue

    if len(dfs) == 0:
        raise ValueError("Aucun fichier *_clean.csv trouvé dans data/clean/. Vérifiez le chemin et les noms des fichiers.")

    df = pd.concat(dfs, ignore_index=True)

    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("é", "e")

    if 'annee' in df.columns:
        df = df.rename(columns={'annee': 'année'})
    
    df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
    df = df.dropna(subset=['valeur', 'latitude', 'longitude'])


    df["indice_qualite_air"] = df.apply(get_air_quality_index, axis=1)

    return df

try:
    df = load_clean_data()
except ValueError as e:
    print(e)
    df = pd.DataFrame(columns=["polluant", "année", "latitude", "longitude", "valeur", "nom_site", "zas", "indice_qualite_air"])


Polluant_ = {"PM10":"PM\u2081\u2080","NO2":"NO\u2082"}

if not df.empty:
    polluants_disponibles = sorted(df["polluant"].unique())
    annees_disponibles = sorted(df["année"].unique())
else:
    polluants_disponibles = []
    annees_disponibles = []


ORDRE_QUALITE = ["BON", "MOYEN", "DÉGRADÉ", "MAUVAIS"]
COULEURS_QUALITE = {
    "BON": "green",
    "MOYEN": "yellow",
    "DÉGRADÉ": "orange",
    "MAUVAIS": "red",
}
    
print("df vide ?", df.empty)
print("annees_disponibles :", annees_disponibles)
print("polluants_disponibles :", polluants_disponibles)
if not df.empty:
    for annee in annees_disponibles:
        for polluant in polluants_disponibles:
            dff = df[(df["année"] == annee) & (df["polluant"] == polluant)]
            if not dff.empty:
                fig = px.scatter_map(
                    dff,
                    lat="latitude",
                    lon="longitude",
                    color="indice_qualite_air",
                    size="valeur",
                    hover_name="nom_site",
                    hover_data={"valeur": True, "zas": True, "latitude": False, "longitude": False},
                    color_discrete_map=COULEURS_QUALITE,
                    category_orders={"indice_qualite_air": ORDRE_QUALITE},
                    size_max=30,
                    zoom=5,
                    height=700,
                    title=f"Indice de la qualité de l'air pour {polluant} en {annee}"
                )
                nom_fichier = f"carte_{polluant}_{annee}.html".replace(" ", "_").replace("₁", "1").replace("₂","2")
                fig.write_html(nom_fichier)
                print(f"Carte interactive sauvegardée sous {nom_fichier}")


def nettoyer_nom_ville(ville):
    """
    Nettoie le nom d'une ville pour créer un nom de fichier valide.

    Remplace les espaces, tirets, barres obliques par des underscores et supprime
    les espaces en début/fin.

    Args:
        ville (str): Le nom de la ville (ZAS) à nettoyer.

    Returns:
        str: Le nom de la ville nettoyé.
    """
    return (
        str(ville)
        .strip()
        .replace(" ", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

import os
os.makedirs("cartes_villes", exist_ok=True)

villes_disponibles = df["zas"].unique()
for ville in villes_disponibles:
    dff = df[df['zas'] == ville]
    if not dff.empty:
        fig = px.scatter_map(
            dff,
            lat="latitude",
            lon="longitude",
            color="indice_qualite_air",
            size="valeur",
            hover_name="zas",
            hover_data={"valeur": True, "zas": True, "latitude": False, "longitude": False},
            color_discrete_map=COULEURS_QUALITE,
            category_orders={"indice_qualite_air": ORDRE_QUALITE},
            size_max=30,
            zoom=10,
            height=600,
            title=f"Qualité de l'air à {ville}"
        )
        fig.write_html(f"cartes_villes/carte_{nettoyer_nom_ville(ville)}.html", include_plotlyjs='inline')


