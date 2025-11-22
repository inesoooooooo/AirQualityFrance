import pandas as pd
import plotly.express as px
import os
import glob # Bibliothèque pour trouver les fichiers

# --- 1. CONFIGURATION ---
# IMPORTANT : Le chemin est maintenant définitif.
DATA_FOLDER = 'data/clean' 

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

# --- 2. COMBINAISON ET PRÉPARATION DES DONNÉES ---
tous_les_dfs = []
print("1. Chargement et combinaison des données...")

# Utilisation de glob pour trouver automatiquement tous les fichiers CSV
# Cette ligne cherche tous les fichiers qui finissent par _clean.csv dans le dossier data/clean
fichiers_a_combiner = glob.glob(os.path.join(DATA_FOLDER, '*_clean.csv'))

if not fichiers_a_combiner:
    print(f"\nERREUR CRITIQUE: Aucun fichier CSV de nettoyage trouvé dans le dossier {DATA_FOLDER}.")
    print("Vérifiez la structure : votre chemin devrait être DossierDuProjet/data/clean/*.csv")
    exit()

for chemin_complet in fichiers_a_combiner:
    try:
        # Tente de lire les fichiers
        df_temp = pd.read_csv(chemin_complet, sep=',', decimal='.') 
        tous_les_dfs.append(df_temp)
    except Exception as e:
        print(f"Erreur lors du traitement de {chemin_complet}: {e}")

if not tous_les_dfs:
    print("Échec du chargement. Script interrompu.")
    exit()

df_global = pd.concat(tous_les_dfs, ignore_index=True)
df_global = df_global.rename(columns={'valeur': 'Concentration', 'Année': 'Annee'})

# Nettoyage et conversion des types
df_global['Concentration'] = pd.to_numeric(df_global['Concentration'], errors='coerce')
df_global['Annee'] = pd.to_numeric(df_global['Annee'], errors='coerce').astype('Int64')

# 2.1 Filtration des polluants et des villes
df_filtre = df_global[
    (df_global['Polluant'].isin(['PM10', 'NO2'])) & 
    (df_global['Zas'].isin(MAP_VILLES.keys()))
].copy()

# 2.2 Remplacement du code ZAG par le nom de la ville (pour l'affichage)
df_filtre['Ville'] = df_filtre['Zas'].map(MAP_VILLES)

# 2.3 Calcul de la moyenne annuelle par ville et par polluant
df_final = df_filtre.groupby(['Annee', 'Polluant', 'Ville'])['Concentration'].mean().reset_index()

print("2. Agrégation des données terminée. Prêt pour la visualisation.")

# --- 3. CRÉATION DU GRAPHIQUE INTERACTIF AVEC PLOTLY ---
fig = px.line(
    df_final,
    x='Annee',
    y='Concentration',
    color='Polluant',       
    line_group='Polluant', 
    facet_col='Ville',      
    facet_col_wrap=3,       
    title="Évolution des concentrations moyennes annuelles (PM10 et NO2) par ville"
)

# Ajuster la mise en page
fig.update_layout(
    xaxis={'dtick': 1}, 
    yaxis_title='Concentration (µg/m³)',
    height=800 
)

# Afficher le graphique interactif dans le navigateur
print("\n3. Affichage du graphique interactif. Une fenêtre de navigateur devrait s'ouvrir.")
fig.show()

fig.write_html("graphique_polluants_par_ville.html") 
print("Graphique interactif sauvegardé sous graphiqe.html")
