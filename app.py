mport streamlit as st
import pandas as pd

st.title("🏘️ Zonalyss - Commune Investment Dashboard")

# Step 1: Property type selection
property_type = st.selectbox("Select Property Type", ["Appartment", "House", "Desk"])

# Step 2: Set file path and score column based on selection
if property_type == "Appartment":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_scores.csv"
    score_column = "zonalyss_score_appartment"
elif property_type == "House":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/house_scores.csv"
    score_column = "zonalyss_score_house"
else:
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/desk_scores.csv"
    score_column = "zonalyss_score_desk"

# Step 3: Load data *after* user makes a selection
@st.cache_data
def load_data(url):
    return pd.read_csv(url)

df = load_data(file_url)

# Debugging helper
st.write("Selected property type:", property_type)
st.write("Score column in use:", score_column)
st.write("Available columns:", df.columns.tolist())

# Step 4: Filter zones by score
if score_column in df.columns:
    min_score = st.slider("Minimum Zonalyss Score", min_value=0, max_value=100, value=50)
    df_filtered = df[df[score_column] >= min_score]
    st.dataframe(df_filtered)
else:
    st.error(f"Score column '{score_column}' not found in file. Please check the file structure.")
