import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Zonalyss Score Map", layout="wide")

# Title
st.title("Zonalyss Investment Score Dashboard")

# Sidebar property type selector
property_type = st.sidebar.selectbox("Select property type", ["Apartment", "House", "Desk"])

# Load the appropriate file and score column
if property_type == "Apartment":
    df = pd.read_csv("https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_scores.csv")
    score_column = "zonalyss_score_appartement"
elif property_type == "House":
    df = pd.read_csv("https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/house_scores.csv")
    score_column = "zonalyss_score_house"
else:
    df = pd.read_csv("https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/desk_scores.csv")
    score_column = "zonalyss_score_desk"

# Filter out rows with missing score
df = df[df[score_column].notna()]

# Display the score table
st.subheader("Commune Zonalyss Scores")
st.dataframe(df[["commune", score_column]])

# Plot the scores as a bar chart
st.subheader(f"{property_type} Zonalyss Score by Commune")
fig = px.bar(df.sort_values(score_column, ascending=False), x="commune", y=score_column,
             labels={score_column: "Zonalyss Score"}, height=500)
st.plotly_chart(fig, use_container_width=True)
