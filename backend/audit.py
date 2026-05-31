import pandas as pd
import json

path = 'D:/2026/pangan-ai/panganai/backend/data/final_training_dataset_feature_engineered.csv'

df = pd.read_csv(path, low_memory=False)

df_bawang = df[df['komoditas'].str.contains('bawang merah', case=False, na=False)]

jenis_harga_counts = df_bawang['jenis_harga'].value_counts().to_dict()

prov_coverage = df_bawang.groupby('jenis_harga')['provinsi'].nunique().to_dict()

date_coverage = df_bawang.groupby('jenis_harga')['tanggal'].nunique().to_dict()

result = {
    "jenis_harga_counts": jenis_harga_counts,
    "provinsi_coverage": prov_coverage,
    "date_coverage": date_coverage,
}

print(json.dumps(result, indent=2))
