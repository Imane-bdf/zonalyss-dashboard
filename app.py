
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Zonalyss Dashboard", layout="wide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/final_scores_with_tags.csv"
    return pd.read_csv(url)

df = load_data()

st.title("📊 Zonalyss - Commune Investment Dashboard")

# Preview raw data
st.subheader("🧾 Raw CSV Preview")
st.dataframe(df.head(20))

# Debug info
st.write("🔍 Available Zone Quality Tags:", df['zone_quality_tag'].unique())
st.write("🔍 ROI Column Type:", df['rental_roi_percent'].dtype)

# Filter options
min_roi = st.slider("Minimum Rental ROI (%)", 0, 100, 5)

valid_tags = df['zone_quality_tag'].dropna()
valid_tags = valid_tags[~valid_tags.isin(['value'])].unique().tolist()

# Set default only if it exists
default_tags = [tag for tag in ['High', 'Medium'] if tag in valid_tags]
if not default_tags:
    default_tags = valid_tags[:2]  # fallback to first two options

selected_tags = st.multiselect("Zone Quality", options=valid_tags, default=default_tags)

# Safe filtering
filtered_df = df.copy()
filtered_df['rental_roi_percent'] = pd.to_numeric(filtered_df['rental_roi_percent'], errors='coerce')
filtered_df = filtered_df[filtered_df['rental_roi_percent'] >= min_roi]
filtered_df = filtered_df[filtered_df['zone_quality_tag'].isin(selected_tags)]

# Display filtered results
st.subheader("📍 Filtered Zones")
st.dataframe(filtered_df.sort_values(by='zonalyss_score', ascending=False).reset_index(drop=True))
st.write('Filtred rows count:' len(filtred_df))

# Download button
st.download_button(
    label="📥 Download Filtered Results as CSV",
    data=filtered_df.to_csv(index=False).encode('utf-8'),
    file_name='zonalyss_filtered_communes.csv',
    mime='text/csv'
)
