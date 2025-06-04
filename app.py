# Load all scores
a_df = pd.read_csv("/content/drive/MyDrive/Zonalyss_Project/Output/final_apartment_scores.csv")
h_df = pd.read_csv("/content/drive/MyDrive/Zonalyss_Project/Output/final_house_scores.csv")
d_df = pd.read_csv("/content/drive/MyDrive/Zonalyss_Project/Output/final_desk_scores.csv")

# Keep commune and score only
a_df = a_df[['commune', 'zonalyss_score_apartment']]
h_df = h_df[['commune', 'zonalyss_score_house']]
d_df = d_df[['commune', 'zonalyss_score_desk']]

# Merge on commune
merged = a_df.merge(h_df, on="commune", how="outer").merge(d_df, on="commune", how="outer")
merged.sort_values("commune").reset_index(drop=True)
