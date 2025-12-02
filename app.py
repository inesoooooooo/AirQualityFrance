import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
import glob
import numpy as np

# -----------------------------------------------------------
# Fonction de classification Indice ATMO officiel Français en 4 niveaux
# Ces seuils sont basés sur l'indice ATMO Français pour les polluants NO2 ET PM10.
# -----------------------------------------------------------

def get_air_quality_index(row):
    """
    Classifie une concentration de polluant (valeur) selon l'indice ATMO simplifié.
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

    # Définition des seuils (en µg/m³) pour les 4 catégories (Bon, Moyen, Dégradé, Mauvais)
    seuils = {
        # NO2 - Dioxyde d'azote 
        "NO2": {
            "BON": 40,
            "MOYEN": 80,
            "DÉGRADÉ": 180,
            "MAUVAIS": np.inf
        },
        
        # PM10 - Particules
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
    
    # Logique de classification
    if valeur <= seuil["BON"]:
        return "BON"
    elif valeur <= seuil["MOYEN"]:
        return "MOYEN"
    elif valeur <= seuil["DÉGRADÉ"]:
        return "DÉGRADÉ"
    else:
        return "MAUVAIS"


# -----------------------------------------------------------
# 🔶 1. Chargement automatique et Nettoyage des données
# -----------------------------------------------------------

def load_clean_data(folder="data/clean/"):
    """
    Charge et nettoie les données d'un dossier spécifié.

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
        raise ValueError("⚠ Aucun fichier *_clean.csv trouvé dans data/clean/. Vérifiez le chemin et les noms des fichiers.")

    df = pd.concat(dfs, ignore_index=True)

    # Standardisation des colonnes
    df.columns = df.columns.str.lower().str.replace(" ", "_").str.replace("é", "e")

    # Correction du nom de la colonne année si besoin
    if 'annee' in df.columns:
        df = df.rename(columns={'annee': 'année'})
    
    # Conversion en numérique
    df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
    df = df.dropna(subset=['valeur', 'latitude', 'longitude'])

    # Créer la colonne Indice Qualité Air
    df["indice_qualite_air"] = df.apply(get_air_quality_index, axis=1)

    return df

# Gérer l'exception si le chargement échoue
try:
    df = load_clean_data()
except ValueError as e:
    print(e)
    # Créer un DataFrame vide pour ne pas bloquer le site
    df = pd.DataFrame(columns=["polluant", "année", "latitude", "longitude", "valeur", "nom_site", "zas", "indice_qualite_air"])

# -----------------------------------------------------------
# 🔶 2. Récupération des valeurs pour les dropdowns et couleurs
# -----------------------------------------------------------

Polluant_ = {
    "PM10":"PM\u2081\u2080",
    "NO2":"NO\u2082"
}
if not df.empty:
    polluants_disponibles = sorted(df["polluant"].unique())
    annees_disponibles = sorted(df["année"].unique())
else:
    polluants_disponibles = []
    annees_disponibles = []

# Définir l'ordre et les couleurs pour l'Indice Qualité Air (Vert/Jaune/Orange/Rouge)
ORDRE_QUALITE = ["BON", "MOYEN", "DÉGRADÉ", "MAUVAIS"]
COULEURS_QUALITE = {
    "BON": "green",
    "MOYEN": "yellow",
    "DÉGRADÉ": "orange",
    "MAUVAIS": "red",
}

# -----------------------------------------------------------
# 🔶 3. Application Dash et Layout
# -----------------------------------------------------------

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Carte interactive de la qualité de l'air en France métropolitaine", 
            style={"textAlign": "center", "marginBottom": "20px"}),

    html.Div([
        # Slider pour l'année (comme sur le croquis)
        html.Div([
            html.Label("Choix de l'année :", style={'marginBottom': '10px'}),
            dcc.Slider(
                id="annee",
                min=annees_disponibles[0] if annees_disponibles else 2020,
                max=annees_disponibles[-1] if annees_disponibles else 2024,
                step=1,
                value=annees_disponibles[-1] if annees_disponibles else 2022,
                marks={str(y): str(y) for y in annees_disponibles} if annees_disponibles else None,
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={"width": "45%", "display": "inline-block", "padding": "10px"}),

        # Dropdown pour le polluant
        html.Div([
            html.Label("Choisissez un polluant :"),
            dcc.Dropdown(
                id="polluant",
                options=[{"label": p, "value": p} for p in polluants_disponibles],
                value="PM2.5" if "PM2.5" in polluants_disponibles else polluants_disponibles[0] if polluants_disponibles else None,
                clearable=False
            )
        ], style={"width": "45%", "display": "inline-block", "padding": "10px"}),
    ]),

    dcc.Graph(id="carte_pollution", style={"height": "800px"}),

    # Légende statique Indice Qualité Air (pour ressembler au croquis)
    html.Div([
        html.H3("Qualité de l'air (Indice ATMO simplifié)", style={"textAlign": "center", "marginTop": "20px"}),
        #Niveaux de qualité de l'air
        html.Ul(
            [
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["BON"], "fontSize": "20px", "marginRight": "10px"}), "BON"], style={"listStyle": "none"}),
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["MOYEN"], "fontSize": "20px", "marginRight": "10px"}), "MOYEN"], style={"listStyle": "none"}),
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["DÉGRADÉ"], "fontSize": "20px", "marginRight": "10px"}), "DÉGRADÉ"], style={"listStyle": "none"}),
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["MAUVAIS"], "fontSize": "20px", "marginRight": "10px"}), "MAUVAIS"], style={"listStyle": "none"}),
            ], 
            style={"textAlign": "center", "padding": "0"}
        ),
        #Polluants (pour bien les afficher)
        html.H4("Polluants", style={"textAlign": "center", "marginTop": "10px"}),
        html.Ul(
            [
                html.Li("NO₂", style={"textAlign": "center", "listStyle": "none"}),
                html.Li("PM₁₀", style={"textAlign": "center", "listStyle": "none"})
            ]
        )
    ]),

], style={"fontFamily": "Arial", "padding": "20px"})


# -----------------------------------------------------------
# 🔶 4. Callback pour mettre à jour la carte
# -----------------------------------------------------------

@app.callback(
    Output("carte_pollution", "figure"),
    Input("annee", "value"),
    Input("polluant", "value")
)
def update_map(annee, polluant):
    """
    Met à jour la carte interactive en fonction de l'année et du polluant sélectionnés.

    Args:
        annee (int): L'année sélectionnée via le slider.
        polluant (str): Le polluant sélectionné via le dropdown.

    Returns:
        dict: Un objet figure Plotly (dictionnaire) pour le composant dcc.Graph.
              Retourne un layout vide si les données sont manquantes ou filtrées.
    """
    if df.empty or annee is None or polluant is None:
        return {}
    
    dff = df[(df["année"] == annee) & (df["polluant"] == polluant)]
    
    if dff.empty: #pour pas que le graphique plante si on a pas de donnée pour un polluant sur une année
        return {
            'layout': {
                'title': f"Aucune donnée pour {polluant} en {annee}",
                'height': 700
            }
        }

    fig = px.scatter_map(
        dff,
        lat="latitude",
        lon="longitude",
        # Utilise l'indice catégoriel pour la couleur
        color="indice_qualite_air", 
        size="valeur",
        hover_name="nom_site",
        hover_data={"valeur": True, "zas": True, "latitude": False, "longitude": False},
        # Force les couleurs Vert/Jaune/Orange/Rouge
        color_discrete_map=COULEURS_QUALITE, 
        # Force l'ordre de la légende
        category_orders={"indice_qualite_air": ORDRE_QUALITE}, 
        size_max=30,
        zoom=5,
        height=700,
        title=f"Indice de la qualité de l'air pour le polluant {polluant} en {annee} en France métropolitaine"
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": 46.603354, "lon": 1.888334},
        margin={"l": 0, "r": 0, "t": 50, "b": 0}
    )
    return fig
    
print("df vide ?", df.empty)
print("annees_disponibles :", annees_disponibles)
print("polluants_disponibles :", polluants_disponibles)
#générer le fichier html
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
                
# -----------------------------------------------------------
# 🔶 5. Génération des cartes par villes
# -----------------------------------------------------------

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
    # on nettoie le nom des villes pour générer des noms de fichiers valides et qui vont pas faire beuguer le code
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


# -----------------------------------------------------------
# 🔶 6. Lancement
# -----------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)
