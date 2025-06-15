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
        "url": "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_scores.csv",
        "score_column": "zonalyss_score_apartment"
    },
    "House": {
        "url": "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/house_scores.csv",
        "score_column": "zonalyss_score_house"
    },
    "Desk": {
        "url": "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/desk_scores.csv",
        "score_column": "zonalyss_score_desk"
    }
}

# Get selected config
config = data_sources.get(property_type)
df = pd.read_csv(config["url"])
score_column = config["score_column"]

# Filter out rows with missing score
df = df[df[score_column].notna()]

# Display explanation
st.markdown("""
#### What is the Zonalyss Score?
The Zonalyss Score (0–100) is a custom investment indicator based on key variables like price trends, ROI, rental yield, and zone quality. A higher score means better investment potential for the selected property type.
""")

# Show raw score table
st.subheader("Commune Zonalyss Scores")
st.dataframe(df[["commune", score_column]].sort_values(by=score_column, ascending=False))

# Show top 5 communes
st.markdown("### 🏆 Top 5 Communes to Invest In")
top_zones = df.sort_values(by=score_column, ascending=False).head(5)
st.dataframe(top_zones[["commune", score_column]])

# Show bar chart
st.subheader(f"{property_type} Zonalyss Scores")
df_sorted = df.sort_values(by=score_column, ascending=False)
fig = px.bar(df_sorted, x="commune", y=score_column,
             title=f"{property_type} Zonalyss Scores by Commune",
             labels={score_column: "Zonalyss Score"})
st.plotly_chart(fig)
