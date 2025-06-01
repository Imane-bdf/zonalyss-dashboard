import streamlit as st
import pandas as pd

st.set_page_config(page_title="Zonalyss Dashboard", layout="wide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/final_scores_with_tags.csv"
    return pd.read_csv(url)

df = load_data()

st.title("📊 Zonalyss - Commune Investment Dashboard")

# Print data ROI range
st.write("📉 Min ROI in data:", df['rental_roi_percent'].min())
st.write("📈 Max ROI in data:", df['rental_roi_percent'].max())
st.write("🧮 Sample ROI values:", df['rental_roi_percent'].dropna().head(10).tolist())

# Preview raw data
st.subheader("🧾 Raw CSV Preview")
st.dataframe(df.head(20))

# ROI column check
st.write("🔍 ROI Column Type:", df['rental_roi_percent'].dtype)

# Filter sidebar
st.sidebar.header("📊 Filters")
min_roi = st.sidebar.slider("Minimum Rental ROI (%)", 0, 100, 5)

# Zone tags filter setup
valid_tags = df['zone_quality_tag'].dropna()
valid_tags = valid_tags[~valid_tags.isin(['value'])].unique().tolist()
st.write("🧭 Available Zone Tags in Data:", valid_tags)

default_tags = [tag for tag in ['High', 'Medium', 'Low'] if tag in valid_tags]
if not default_tags:
    default_tags = valid_tags[:2]  # fallback if nothing matches

selected_tags = st.sidebar.multiselect("Zone Quality", options=valid_tags, default=default_tags)
st.write("✅ Selected Tags:", selected_tags)

# Apply filters safely
try:
    filtered_df = df.copy()
    filtered_df['rental_roi_percent'] = pd.to_numeric(filtered_df['rental_roi_percent'], errors='coerce')
    filtered_df = filtered_df[filtered_df['rental_roi_percent'] >= min_roi]
    filtered_df = filtered_df[filtered_df['zone_quality_tag'].isin(selected_tags)]

    # Output diagnostics
    st.subheader("📍 Filtered Zones")
    st.write("📌 ROI Filter Used:", min_roi)
    st.write("🧮 Matching Rows:", len(filtered_df))
    st.write("📌 Filtered Data Preview:")
    st.dataframe(filtered_df.sort_values(by='zonalyss_score', ascending=False).reset_index(drop=True).head(10))

    st.download_button(
        label="📥 Download Filtered Results as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='zonalyss_filtered_communes.csv',
        mime='text/csv'
    )
except Exception as e:
    st.error(f"❌ Error filtering data: {e}")
    st.write("💡 Try resetting the filters or verifying column names.")
