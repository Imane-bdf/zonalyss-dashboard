
Imane Charifa Beddiaf <beddiaf.imane.charifa@gmail.com>
18:49 (il y a 0 minute)
À moi

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

st.set_page_config(layout="wide")

# --- DATA LOAD ---
# Apartment scores CSV (GitHub raw link)
csv_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/refs/heads/main/appartement_scores_simulated.csv"
df = pd.read_csv(csv_url)

# Luxembourg communes GeoJSON (GitHub raw link)
geojson_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/refs/heads/main/luxembourg_communes_real.geojson"
geojson_data = requests.get(geojson_url).json()

# --- DEBUG: Display communes to check matching ---
st.sidebar.header("Debug Info (first 10 values)")
st.sidebar.write("CSV communes:", df["commune"].unique()[:10])
st.sidebar.write("GeoJSON communes:", [f['properties']['commune'] for f in geojson_data['features'][:10]])

# --- MAP ---
score_column = "zonalyss_score_apartment" # Make sure this matches your CSV

fig = px.choropleth_mapbox(
    df,
    geojson=geojson_data,
    locations="commune",
    featureidkey="properties.commune",
    color=score_column,
    color_continuous_scale="Viridis",
    mapbox_style="carto-positron",
    zoom=8,
    center={"lat": 49.8153, "lon": 6.1296},
    opacity=0.65,
    labels={score_column: "Zonalyss Score"},
    hover_name="commune"
)

st.title("Zonalyss Apartment Investment Map – Luxembourg")
st.plotly_chart(fig, use_container_width=True)

# --- Optionally: Show ranked list of communes
st.header("Top 10 Communes by Zonalyss Score")
st.dataframe(df[["commune", score_column]].sort_values(score_column, ascending=False).head(10), use_container_width=True)
