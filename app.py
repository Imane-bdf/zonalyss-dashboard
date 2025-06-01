
import streamlit as st
import pandas as pd

st.title("🏙️ Zonalyss – Commune Investment Scores")
st.caption("Luxembourg pilot version – Rental ROI + Zone Quality")

@st.cache_data
def load_data():
    return pd.read_csv("final_scores_with_tags.csv")

df = load_data()

st.sidebar.header("🔎 Filter Zones")
min_roi = st.sidebar.slider("Minimum Rental ROI %", 0.0, 15.0, 5.0, step=0.5)
selected_tags = st.sidebar.multiselect("Zone Quality", df['zone_quality_tag'].unique(), default=['High', 'Medium'])

filtered_df = df[
    (df['rental_roi_percent'] >= min_roi) &
    (df['zone_quality_tag'].isin(selected_tags))
]

st.subheader("📊 Filtered Commune Scores")
st.dataframe(filtered_df[['commune', 'rental_roi_percent', 'zone_quality_tag', 'zonalyss_score']])

st.download_button(
    label="📥 Download Results as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='zonalyss_filtered_communes.csv',
    mime='text/csv'
)
