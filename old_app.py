import streamlit as st
import pandas as pd

st.set_page_config(page_title="Zonalyss Dashboard", layout="wide")

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Imane-bdf/zonalyss-dashboard/main/final_scores_with_tags.csv"
    return pd.read_csv(url)

df = load_data()

st.title("📊 Zonalyss - Commune Investment Dashboard")

# Diagnostic ROI values
st.write("📉 Min ROI in data:", df['rental_roi_percent'].min())
st.write("📈 Max ROI in data:", df['rental_roi_percent'].max())
st.write("🧮 Sample ROI values:", df['rental_roi_percent'].dropna().head(10).tolist())

# Filter sidebar
st.sidebar.header("📊 Filters")
min_roi = st.sidebar.slider("Minimum Rental ROI (%)", -100, 100, -70)

# Zone tags
valid_tags = df['zone_quality_tag'].dropna()
valid_tags = valid_tags[~valid_tags.isin(['value'])].unique().tolist()
default_tags = [tag for tag in ['High', 'Medium', 'Low'] if tag in valid_tags]
if not default_tags:
    default_tags = valid_tags[:2]
selected_tags = st.sidebar.multiselect("Zone Quality", options=valid_tags, default=default_tags)

# Apply filters
try:
    df['rental_roi_percent'] = pd.to_numeric(df['rental_roi_percent'], errors='coerce')
    filtered_df = df[
        (df['rental_roi_percent'] >= min_roi) &
        (df['zone_quality_tag'].isin(selected_tags))
    ]

    # Summary section
    st.subheader("📌 Summary Stats")
    if not filtered_df.empty:
        avg_roi = round(filtered_df['rental_roi_percent'].mean(), 2)
        top_zone = filtered_df.loc[filtered_df['zonalyss_score'].idxmax()]
        st.metric("📈 Average ROI (%)", f"{avg_roi}")
        st.metric("🏅 Top Zone", f"{top_zone['commune']} ({round(top_zone['zonalyss_score'], 2)})")
        st.metric("📍 Zones Matching Filter", len(filtered_df))
    else:
        st.write("⚠️ No zones match the current filters.")

    # Display results
    st.subheader("📍 Filtered Zones")
    st.dataframe(filtered_df.sort_values(by='zonalyss_score', ascending=False).reset_index(drop=True))

    # Download option
    st.download_button(
        label="📥 Download Filtered Results as CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name='zonalyss_filtered_communes.csv',
        mime='text/csv'
    )

except Exception as e:
    st.error(f"❌ Error: {e}")
