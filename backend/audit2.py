import pandas as pd
import json

path = 'D:/2026/pangan-ai/panganai/backend/data/final_training_dataset_feature_engineered.csv'

df = pd.read_csv(path, low_memory=False)

# Check all commodities for 'pasar_tradisional' coverage
df_pasar = df[df['jenis_harga'] == 'pasar_tradisional']

# Total unique provinces in the dataset overall
total_provinces = df['provinsi'].nunique()
# Total unique dates in the dataset overall
total_dates = df['tanggal'].nunique()

commodity_coverage = {}
for komoditas in df['komoditas'].dropna().unique():
    subset = df_pasar[df_pasar['komoditas'] == komoditas]
    provs = subset['provinsi'].nunique()
    dates = subset['tanggal'].nunique()
    commodity_coverage[komoditas] = {
        "provinces": provs,
        "dates": dates,
        "total_provinces_possible": total_provinces,
        "total_dates_possible": total_dates
    }

print(json.dumps(commodity_coverage, indent=2))
