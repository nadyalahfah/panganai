import pandas as pd
import json

path = 'D:/2026/pangan-ai/panganai/backend/data/final_training_dataset_feature_engineered.csv'

df = pd.read_csv(path, low_memory=False)

all_provinces = set(df['provinsi'].dropna().unique())
all_commodities = set(df['komoditas'].dropna().unique())

missing_info = {}
total_cells = len(all_provinces) * len(all_commodities)
covered_cells = 0

for komoditas in all_commodities:
    df_kom = df[df['komoditas'] == komoditas]
    
    # Provinces that have pasar_tradisional
    df_pasar = df_kom[df_kom['jenis_harga'] == 'pasar_tradisional']
    covered_provs = set(df_pasar['provinsi'].dropna().unique())
    covered_cells += len(covered_provs)
    
    missing_provs = all_provinces - covered_provs
    
    if missing_provs:
        prov_details = {}
        for p in missing_provs:
            df_missing_p = df_kom[df_kom['provinsi'] == p]
            available_tiers = df_missing_p['jenis_harga'].dropna().unique().tolist()
            prov_details[p] = available_tiers
        
        missing_info[komoditas] = {
            "total_covered": len(covered_provs),
            "total_missing": len(missing_provs),
            "missing_provinces": prov_details
        }

coverage_percentage = (covered_cells / total_cells) * 100

result = {
    "total_provinces": len(all_provinces),
    "total_commodities": len(all_commodities),
    "strict_mode_coverage_pct": round(coverage_percentage, 2),
    "incomplete_commodities": missing_info
}

print(json.dumps(result, indent=2))
