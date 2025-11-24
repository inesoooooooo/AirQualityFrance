import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import glob
from collections import OrderedDict

# --- 1. CONFIGURATION ---
DATA_FOLDER = '../data/clean'

# Correspondance entre le code ZAG dans les données et le nom de la ville
MAP_VILLES = {
    'ZAG LYON': 'Lyon',
    'ZAG BORDEAUX': 'Bordeaux',
    'ZAG TOULOUSE': 'Toulouse',
    'ZAG MARSEILLE-AIX': 'Marseille-Aix',
    'ZAG NICE': 'Nice',
    'ZAG STRASBOURG': 'Strasbourg',
    'ZAG RENNES': 'Rennes'
}

# --- 2. COMBINAISON ET PRÉPARATION DES DONNÉES (Identique à l'original) ---
tous_les_dfs = []
print("1. Chargement et combinaison des données...")

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

# Filtration des polluants et des villes
df_filtre = df_global[
    (df_global['Polluant'].isin(['PM10', 'NO2'])) & 
    (df_global['Zas'].isin(MAP_VILLES.keys()))
].copy()

df_filtre['Ville'] = df_filtre['Zas'].map(MAP_VILLES)

# Calcul de la moyenne annuelle par ville, polluant et année
df_final = df_filtre.groupby(['Annee', 'Polluant', 'Ville'])['Concentration'].mean().reset_index()

# Assurer que les années sont bien triées pour le graphique
df_final = df_final.sort_values(by='Annee')

print("2. Agrégation des données terminée. Prêt pour la visualisation.")

# --- 3. CRÉATION DU GRAPHIQUE AVEC BOUTONS DE SÉLECTION ---


villes_disponibles = sorted(df_final['Ville'].unique())
premiere_ville = villes_disponibles[0] if villes_disponibles else None

if not premiere_ville:
    print("Aucune donnée disponible pour créer le graphique.")
    exit()


fig = go.Figure()

# 3.2 Ajouter une trace pour chaque ville
# Chaque trace est visible ou invisible par défaut
for i, ville in enumerate(villes_disponibles):
    df_ville = df_final[df_final['Ville'] == ville]
    
    # Ajout des lignes PM10 et NO2 pour cette ville
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

# 3.3 Créer les boutons de sélection (Updatemenus)
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

# 3.5 Finaliser la mise en page
fig.update_layout(
    title=f"Évolution des concentrations (PM10 et NO2) à {premiere_ville}",
    xaxis={'dtick': 1, 'title': 'Année'},
    yaxis_title='Concentration (µg/m³)',
    height=600
)

# --- 4. EXPORTATION ---
fig.write_html("graphique.html") 
print("\n3. Graphique interactif avec sélecteur sauvegardé sous graphique.html")

fig.show()