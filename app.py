import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import os
import glob
import numpy as np

# -----------------------------------------------------------
# 🛠️ Fonction de classification Indice ATMO (Simplifiée aux 4 niveaux)
# Ces seuils sont basés sur l'indice ATMO Français (simplifié) pour les polluants les plus courants.
# -----------------------------------------------------------

def get_air_quality_index(row):
    """
    Classifie une concentration de polluant (valeur) selon l'indice ATMO simplifié.
    Retourne une des 4 catégories : 'BON', 'MOYEN', 'DÉGRADÉ', 'MAUVAIS'.
    """
    polluant = row['polluant']
    valeur = row['valeur']

    # Définition des seuils (en µg/m³) pour les 4 catégories (Bon, Moyen, Dégradé, Mauvais)
    seuils = {
        # PM2.5 - Particules fines
        "PM2.5": {
            "BON": 10,
            "MOYEN": 25,
            "DÉGRADÉ": 50,
            "MAUVAIS": np.inf  
        },
        # NO2 - Dioxyde d'azote 
        "NO2": {
            "BON": 40,
            "MOYEN": 80,
            "DÉGRADÉ": 180,
            "MAUVAIS": np.inf
        },
        # O3 - Ozone
        "O3": {
            "BON": 80,
            "MOYEN": 120,
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
        # Ajoutez d'autres polluants si nécessaire
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

# ⚠️ Gérer l'exception si le chargement échoue
try:
    df = load_clean_data()
except ValueError as e:
    print(e)
    # Créer un DataFrame vide pour ne pas bloquer l'application
    df = pd.DataFrame(columns=["polluant", "année", "latitude", "longitude", "valeur", "nom_site", "zas", "indice_qualite_air"])

# -----------------------------------------------------------
# 🔶 2. Récupération des valeurs pour les dropdowns et couleurs
# -----------------------------------------------------------

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
    "NON CLASSIFIÉ": "gray"
}

# -----------------------------------------------------------
# 🔶 3. Application Dash et Layout
# -----------------------------------------------------------

app = dash.Dash(__name__)

app.layout = html.Div([

    html.H1("Carte interactive de la qualité de l'air en France", 
            style={"textAlign": "center", "marginBottom": "20px"}),

    html.Div([
        # Slider pour l'année (comme sur le croquis)
        html.Div([
            html.Label("Choisir une année :", style={'marginBottom': '10px'}),
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
            html.Label("Choisir un polluant :"),
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
        html.H3("Indice Qualité Air", style={"textAlign": "center", "marginTop": "20px"}),
        html.Ul(
            [
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["BON"], "fontSize": "20px", "marginRight": "10px"}), "BON"], style={"listStyle": "none"}),
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["MOYEN"], "fontSize": "20px", "marginRight": "10px"}), "MOYEN"], style={"listStyle": "none"}),
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["DÉGRADÉ"], "fontSize": "20px", "marginRight": "10px"}), "DÉGRADÉ"], style={"listStyle": "none"}),
                html.Li([html.Span("●", style={"color": COULEURS_QUALITE["MAUVAIS"], "fontSize": "20px", "marginRight": "10px"}), "MAUVAIS"], style={"listStyle": "none"}),
            ], 
            style={"textAlign": "center", "padding": "0"}
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
    if df.empty or annee is None or polluant is None:
        return {}
    
    dff = df[(df["année"] == annee) & (df["polluant"] == polluant)]
    
    if dff.empty:
        return {
            'layout': {
                'title': f"Aucune donnée pour {polluant} en {annee}",
                'height': 700
            }
        }

    fig = px.scatter_mapbox(
        dff,
        lat="latitude",
        lon="longitude",
        # Utilise l'indice catégoriel pour la couleur
        color="indice_qualite_air", 
        size="valeur",
        hover_name="nom_site",
        hover_data={"année": True, "valeur": True, "zas": True},
        # Force les couleurs Vert/Jaune/Orange/Rouge
        color_discrete_map=COULEURS_QUALITE, 
        # Force l'ordre de la légende
        category_orders={"indice_qualite_air": ORDRE_QUALITE}, 
        size_max=30,
        zoom=5,
        height=700,
        title=f"Indice Qualité Air pour le polluant {polluant} en {annee}"
    )

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox_center={"lat": 46.603354, "lon": 1.888334},
        margin={"l": 0, "r": 0, "t": 50, "b": 0}
    )

    return fig


# -----------------------------------------------------------
# 🔶 5. Lancement
# -----------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
