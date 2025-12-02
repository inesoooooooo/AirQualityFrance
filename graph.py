import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from collections import OrderedDict

DATA_FOLDER = 'data/clean'

# Correspondance entre le code ZAG dans les données et le nom de la ville
MAP_VILLES = {
    'ZAG PARIS': 'Paris',
    'ZAG NANTES-SAINT-NAZAIRE': 'Nantes',
    'ZAG MONTPELLIER': 'Montpellier',
    'ZAG LYON': 'Lyon',
    'ZAG BORDEAUX': 'Bordeaux',
    'ZAG TOULOUSE': 'Toulouse',
    'ZAG MARSEILLE-AIX': 'Marseille-Aix',
    'ZAG NICE': 'Nice',
    'ZAG STRASBOURG': 'Strasbourg',
    'ZAG LILLE': 'Lille'
}

tous_les_dfs = []
print("1. Chargement et combinaison des données...")

def charger_combiner_csv(data_folder: str) -> pd.DataFrame:
    """
    Charge tous les fichiers CSV du dossier des CSV clean et les combine en un seul DataFrame
    Arguments:
    data_folder (str) chemin vers le dossier contenant les CSV clean
    Returns:
    pd.DataFrame: DataFrame combiné avec les colonnes renommées et typses corrects
    """
    fichiers_a_combiner = glob.glob(os.path.join(DATA_FOLDER, '*_clean.csv'))

    if not fichiers_a_combiner:
        print(f"\nERREUR CRITIQUE: Aucun fichier CSV de nettoyage trouvé dans le dossier {DATA_FOLDER}.")
        exit()

    for chemin_complet in fichiers_a_combiner:
        try:
            df_temp = pd.read_csv(chemin_complet, sep=',', decimal='.') 
            tous_les_dfs.append(df_temp)
        except Exception as e:
            print(f"Erreur lors du traitement de {chemin_complet}: {e}")

    if not tous_les_dfs:
        print("Échec du chargement. Script interrompu.")
        exit()

    df_global = pd.concat(tous_les_dfs, ignore_index=True)
    df_global = df_global.rename(columns={'valeur': 'Concentration', 'Année': 'Annee'})
    df_global['Concentration'] = pd.to_numeric(df_global['Concentration'], errors='coerce')
    df_global['Annee'] = pd.to_numeric(df_global['Annee'], errors='coerce').astype('Int64')
    
    return df_global

def filter_agreger(df: pd.DataFrame, map_villes: dict) -> pd.DataFrame:
    """
    Filtre les polluants PM10 et No2 et les villes définies, puis calcule la moyenne annuelle
    Arguments : df (pd.DataFrame) : DataFrame global
    Returns : pd.DataFrame final agrégé par année, polluant et ville
    """
    df_filtre = df_global[
        (df_global['Polluant'].isin(['PM10', 'NO2'])) & 
        (df_global['Zas'].isin(MAP_VILLES.keys()))
    ].copy()

    df_filtre['Ville'] = df_filtre['Zas'].map(MAP_VILLES)
    df_final = df_filtre.groupby(['Annee', 'Polluant', 'Ville'])['Concentration'].mean().reset_index()
    df_final = df_final.sort_values(by='Annee')

    return df_final

print("2. Agrégation des données terminée. Prêt pour la visualisation.")

def creer_graphique(df_final: pd.DataFrame) -> go.Figure:
    """
    Crée un graphique interactif avec Plotly avec un menu déroulant pour sélectionner la ville
    Arguments: df_final (pd.DataFrame): DataFrame agrégé
    Returns : go.Figure: Objet figure Plotly prêt à être affiché ou exporté
    """
    villes_disponibles = sorted(df_final['Ville'].unique())
    premiere_ville = villes_disponibles[0] if villes_disponibles else None

    if not premiere_ville:
        print("Aucune donnée disponible pour créer le graphique.")
        exit()
    
    fig = go.Figure()


    for i, ville in enumerate(villes_disponibles):
        df_ville = df_final[df_final['Ville'] == ville]

        for polluant in ['PM10', 'NO2']:
            df_polluant = df_ville[df_ville['Polluant'] == polluant]
            fig.add_trace(
                go.Scatter(
                    x=df_polluant['Annee'],
                    y=df_polluant['Concentration'],
                    mode='lines+markers',
                    name=f"{polluant}",
                    legendgroup=polluant,  # Groupe de légende commun pour PM10/NO2
                    line=dict(dash='solid' if polluant == 'PM10' else 'dash'),
                    visible=(ville == premiere_ville), # Seule la première ville est visible initialement
                )
            )
     
    boutons_ville = []
    nombre_de_polluants = 2 # PM10 et NO2
    
    for i, ville in enumerate(villes_disponibles):
        visibilite = [False] * len(villes_disponibles) * nombre_de_polluants 
        visibilite[i * nombre_de_polluants : (i + 1) * nombre_de_polluants] = [True, True]
        bouton = dict(
            method='update',
            label=ville,
            args=[
                {'visible': visibilite},
                {'title': f"Évolution des concentrations (PM10 et NO2) à {ville}"}
            ]
        )
        boutons_ville.append(bouton)
        
    fig.update_layout(
        updatemenus=[
            dict(
                type="dropdown",
                direction="down",
                x=0.01,
                y=1.15,
                showactive=True,
                active=0, 
                buttons=boutons_ville,
                font=dict(size=12)
                            
            )
        ]
    )
    fig.update_layout(
        title=f"Évolution des concentrations (PM10 et NO2) à {premiere_ville}",
        xaxis={'dtick': 1, 'title': 'Année'},
        yaxis_title='Concentration (µg/m³)',
        height=600
    )
    return fig

def exporter_graphique (fig: go.Figure, fichier_html: str = "graphique.html"):
    """
    Exporte la figure Plotly en fichier HTML
    Arguments : fig (go.Figure): Figure Plotly
                fichier_html (str): Nom du fichier de sortie HTML
    """
    fig.write_html("graphique.html") 
    print("\n3. Graphique interactif sauvegardé sous graphique.html")

    fig.show()


