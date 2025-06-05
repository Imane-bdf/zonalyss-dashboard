import streamlit as st
import pandas as pd

# App title
st.title("🏘️ Zonalyss – Commune Investment Dashboard")

# Property type selection
property_type = st.selectbox("Select Property Type", ["Appartement", "House", "Desk"])

# Load the appropriate file and score column based on selection
if property_type == "Appartement":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_scores.csv"
    score_column = "zonalyss_score_appartement"
elif property_type == "House":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/house_scores.csv"
    score_column = "zonalyss_score_house"
else: # Desk
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/desk_scores.csv"
    score_column = "zonalyss_score_desk"

# Load the data from the correct CSV
@st.cache_data
def load_data():
    return pd.read_csv(file_url)

df = load_data()

# DEBUG info to help troubleshoot
st.write("Selected property type:", property_type)
st.write("Score column in use:", score_column)
st.write("Available columns:", df.columns.tolist())

# Filter options
st.subheader("🎯 Filter Zones")
min_score = st.slider("Minimum Zonalyss Score", min_value=0, max_value=100, value=50)

if score_column in df.columns:
    df_filtered = df[df[score_column] >= min_score]

    st.subheader("📍 Filtered Zones")
    st.dataframe(df_filtered)

    # Download button
    st.download_button("📥 Download Filtered Results", df_filtered.to_csv(index=False), "filtered_zones.csv")
else:
    st.error(f"Score column '{score_column}' not found in file. Please check the file structure.")

