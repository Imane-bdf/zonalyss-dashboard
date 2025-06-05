import streamlit as st
import pandas as pd

# --- Title ---
st.title("🏢 Zonalyss – Commune Investment Dashboard")

# --- Property Type Selection ---
property_type = st.selectbox("Select Property Type", ["Appartment", "House", "Desk"])

# --- File selection logic ---
if property_type == "Appartment":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/appartement_score.csv"
    score_column = "zonalyss_score_appartment"
elif property_type == "House":
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/final_house_scores.csv"
    score_column = "zonalyss_score_house"
else:
    file_url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/desk_scores.csv"
    score_column = "zonalyss_score_desk"

@st.cache_data
def load_data():
    return pd.read_csv(file_url)

df = load_data()

#debug INFO
st.write('Selected property type:', property_type)
st.write('score column in use:', score_column)
st.write('Available column in file:', df.columns.tolist())

# --- Filter options ---
st.subheader("🎯 Filter Zones")
min_score = st.slider("Minimum Zonalyss Score", min_value=0, max_value=100, value=50)

# Optional: Filter by investment tag (if the column exists)
tag_column = "investment_tag"
if tag_column in df.columns:
    available_tags = df[tag_column].dropna().unique().tolist()
    selected_tags = st.multiselect("Select Investment Tags", options=available_tags, default=available_tags)
    df = df[df[tag_column].isin(selected_tags)]

# Filter by Zonalyss Score
df_filtered = df[df[score_column] >= min_score]

# --- Display table ---
st.subheader("🏘️ Filtered Zones")
st.dataframe(df_filtered.sort_values(score_column, ascending=False).reset_index(drop=True))

# --- Highlight Top Zone ---
if not df_filtered.empty:
    top_zone = df_filtered.sort_values(score_column, ascending=False).iloc[0]
    st.success(f"🏆 Best Zone: **{top_zone['commune']}** — Score: {top_zone[score_column]:.2f}")
else:
    st.warning("⚠️ No zones meet the current filter criteria.")

# --- Download Option ---
csv = df_filtered.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download Filtered Results", csv, f"{property_type}_filtered_results.csv", "text/csv")

