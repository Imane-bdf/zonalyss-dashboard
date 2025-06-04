import streamlit as st
import pandas as pd

# --- Title ---
st.title("🏢 Zonalyss – Commune Investment Dashboard")

# --- Property Type Selection ---
property_type = st.selectbox("Select Property Type", ["Apartment", "House", "Desk"])

# --- File selection logic ---
if property_type == "Apartment":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_final_score_with_tags.csv"
    score_column = "zonalyss_score"
elif property_type == "House":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/final_house_scores.csv"
    score_column = "zonalyss_score_house"
else:
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/final_desk_scores.csv"
    score_column = "zonalyss_score_desk"

@st.cache_data
def load_data():
    return pd.read_csv(file_url)

df = load_data()
