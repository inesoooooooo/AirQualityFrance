import pandas as pd
import plotly.express as px

df = pd.read_csv("data/test/air_quality_france.csv")
def carte_pollution(annee=2024, polluant="NO2"):
    data = df[(df["annee"] == annee) & (df["polluant"] == polluant)]

    fig = px.scatter_mapbox(
        data,
        lat="latitude",
        lon="longitude",
        color="valeur",
        size="valeur",
        hover_name="nom_com",
        hover_data={"annee": True, "valeur": True},
        color_continuous_scale="RdYlGn_r",
        size_max=30, 
        zoom=5,  
        height=600,
        title=f"Niveau de {polluant} en {annee}"
    )

    fig.update_layout(
    mapbox_style="open-street-map",
    mapbox_center={"lat": 46.603354, "lon": 1.888334},
    mapbox=dict(
        bearing=0,
        pitch=0
    )
)


    return fig




