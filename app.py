import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zonalyss Score Map", layout="wide")
st.title("Zonalyss Investment Score Dashboard")

# Sidebar selector
property_type = st.sidebar.selectbox("Select property type", ["Apartment", "House", "Desk"])

# Mapping property type to data source and score column
data_sources = {
    "Apartment": {
        "url": "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_scores_simulated.csv",
        "score_column": "zonalyss_score_apartment"
    },
    "House": {
        "url": "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/house_scores_simulated.csv",
        "score_column": "zonalyss_score_house"
    },
    "Desk": {
        "url": "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/desk_scores_simulated.csv.csv",
        "score_column": "zonalyss_score_desk"
    }
}

# Get selected config
config = data_sources.get(property_type)
df = pd.read_csv(config["url"])
score_column = config["score_column"]

# Debug info
st.write("Selected property type:", property_type)
st.write("Expected score column:", score_column)
st.write("Available columns in data:", df.columns.tolist())

# Prevent KeyError
if score_column not in df.columns:
    st.error(f"Column '{score_column}' not found in CSV. Please check the file.")
    st.stop()

# Filter valid scores
df = df[df[score_column].notna()]

# Show table
st.subheader("Commune Zonalyss Scores")
st.dataframe(df[["commune", score_column]])

# Plot
fig = px.bar(df, x="commune", y=score_column, title=f"{property_type} Zonalyss Scores")
st.plotly_chart(fig, use_container_width=True)
