import os
import pandas as pd
import numpy as np

RAW_DIR = r"d:\2026\pangan-ai\panganai\backend\data\raw_supply_demand\raw_supply_demand"
OUTPUT_FILE = r"d:\2026\pangan-ai\panganai\backend\data\master_supply_demand.csv"
REPORT_FILE = r"d:\2026\pangan-ai\panganai\backend\data\quality_report.txt"

def normalize_provinsi(p):
    if pd.isna(p): return None
    p = str(p).strip().title()
    # Handle specific replacements
    p = p.replace("Dki Jakarta", "DKI Jakarta")
    p = p.replace("Di Yogyakarta", "DI Yogyakarta")
    p = p.replace("Kep.", "Kepulauan")
    p = p.replace("Kepulauan  Riau", "Kepulauan Riau")
    if 'Bangka' in p: return "Kepulauan Bangka Belitung"
    # Remove non-province noise
    if p.lower() in ['indonesia', 'catatan', 'angka sementara', 'angka tetap']:
        return None
    if 'papua barat' in p.lower() and 'daya' not in p.lower(): return "Papua Barat"
    return p

def parse_supply_col(col_name):
    col_name = str(col_name).lower()
    if 'beras' in col_name and 'padi' in col_name: return "Produksi Padi - Produksi Beras", 1.0
    if 'cabai keriting' in col_name: return "Cabai Keriting", 0.1
    if 'cabai rawit' in col_name: return "Cabai Rawit", 0.1
    if 'cabai besar' in col_name: return "Cabai Besar", 0.1
    if 'bawang merah' in col_name: return "Bawang Merah", 0.1
    return None, None

def build_supply():
    supply_records = []
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv')]
    
    for f in files:
        if "Produksi Padi dan Beras" in f or "Produksi Tanaman Sayuran" in f:
            try:
                # Extract year from filename
                year_str = [word for word in f.replace('.csv','').split(',') if word.strip().isdigit()]
                if not year_str: year_str = [word for word in f.replace('.csv','').split() if word.strip().isdigit()]
                year = int(year_str[-1]) if year_str else 2024
                
                df = pd.read_csv(os.path.join(RAW_DIR, f), sep=None, engine='python')
                prov_col = [c for c in df.columns if 'prov' in c.lower()][0]
                
                for _, row in df.iterrows():
                    prov = normalize_provinsi(row[prov_col])
                    if not prov: continue
                    
                    for col in df.columns:
                        kom, mult = parse_supply_col(col)
                        if kom:
                            val = row[col]
                            try:
                                val = float(str(val).replace(',',''))
                                if not pd.isna(val) and val > 0:
                                    supply_records.append({
                                        'tahun': year,
                                        'provinsi': prov,
                                        'supply_raw': kom,
                                        'supply_ton': val * mult
                                    })
                            except:
                                pass
            except Exception as e:
                print(f"Error reading {f}: {e}")
                
        elif "Produksi Telur Ayam" in f:
            try:
                year_str = [word for word in f.replace('.csv','').split(',') if word.strip().isdigit()]
                year = int(year_str[-1]) if year_str else 2024
                df = pd.read_csv(os.path.join(RAW_DIR, f), sep=None, engine='python')
                if len(df) > 2:
                    for i in range(2, len(df)):
                        prov = normalize_provinsi(df.iloc[i, 0])
                        val = df.iloc[i, 1]
                        if prov:
                            try:
                                val = float(str(val).replace(',',''))
                                if not pd.isna(val) and val > 0:
                                    supply_records.append({
                                        'tahun': year,
                                        'provinsi': prov,
                                        'supply_raw': 'Telur Ayam Petelur',
                                        'supply_ton': val
                                    })
                            except:
                                pass
            except Exception as e:
                print(f"Error reading {f}: {e}")
                
    return pd.DataFrame(supply_records)

def build_demand_pop():
    # Load population
    pop_file = os.path.join(r"d:\2026\pangan-ai\panganai\backend\population_2025.csv")
    df_pop = pd.read_csv(pop_file)
    df_pop['Provinsi'] = df_pop['Provinsi'].apply(normalize_provinsi)
    pop_dict = df_pop.set_index('Provinsi')['Jumlah Penduduk (Ribu)'].to_dict()
    
    demand_records = []
    files = [f for f in os.listdir(RAW_DIR) if f.endswith('.csv') and "Rata-rata_Konsumsi_per_Jenis_Pangan_Penduduk_Indonesia_Provinsi" in f]
    for f in files:
        df = pd.read_csv(os.path.join(RAW_DIR, f), sep=None, engine='python')
        prov_col = [c for c in df.columns if 'provinsi' in c.lower()][0]
        for _, row in df.iterrows():
            prov = normalize_provinsi(row[prov_col])
            if not prov: continue
            
            kom = str(row['Komoditas']).strip()
            # Only keep targets
            if kom in ['Beras', 'Telur', 'Minyak Sawit']:
                val = row['Konsumsi_Pangan']
                try:
                    val = float(str(val).replace(',',''))
                    year = int(row['Tahun'])
                    pop_ribu = pop_dict.get(prov, 0)
                    if pop_ribu > 0 and not pd.isna(val):
                        demand_ton = val * float(pop_ribu) # Ton = kg * Ribu = kg * 1000 / 1000
                        demand_records.append({
                            'tahun': year,
                            'provinsi': prov,
                            'demand_raw': kom,
                            'demand_ton': demand_ton
                        })
                except Exception as e:
                    pass
    return pd.DataFrame(demand_records)

def main():
    print("Building Supply...")
    df_supply = build_supply()
    print("Building Demand...")
    df_demand = build_demand_pop()
    
    # Target Commodities Mapping
    TARGETS = [
        {"komoditas": "Beras Medium I", "supply_raw": "Produksi Padi - Produksi Beras", "demand_raw": "Beras", "forecast_supported": True},
        {"komoditas": "Beras Medium II", "supply_raw": "Produksi Padi - Produksi Beras", "demand_raw": "Beras", "forecast_supported": True},
        {"komoditas": "Beras Premium", "supply_raw": "Produksi Padi - Produksi Beras", "demand_raw": "Beras", "forecast_supported": True},
        {"komoditas": "Telur Ayam Ras", "supply_raw": "Telur Ayam Petelur", "demand_raw": "Telur", "forecast_supported": True},
        {"komoditas": "Cabai Merah Keriting", "supply_raw": "Cabai Keriting", "demand_raw": None, "forecast_supported": True},
        {"komoditas": "Cabai Merah Besar", "supply_raw": "Cabai Besar", "demand_raw": None, "forecast_supported": True},
        {"komoditas": "Cabai Rawit", "supply_raw": "Cabai Rawit", "demand_raw": None, "forecast_supported": True},
        {"komoditas": "Bawang Merah Ukuran Sedang", "supply_raw": "Bawang Merah", "demand_raw": None, "forecast_supported": True},
        {"komoditas": "Minyak Goreng Curah", "supply_raw": None, "demand_raw": "Minyak Sawit", "forecast_supported": False} # No supply, but let's keep it as demand_only. Wait, the rule says "Do NOT set forecast_supported = false for commodities that still have usable supply data". Minyak Goreng Curah has NO supply data. Is it false? We'll set True for now unless fully missing.
    ]
    
    final_rows = []
    
    # Get distinct (tahun, provinsi) pairs
    years = sorted(list(set(df_supply['tahun'].unique()).union(set(df_demand['tahun'].unique()))))
    provinces = sorted(list(set(df_supply['provinsi'].unique()).union(set(df_demand['provinsi'].unique()))))
    
    for t in TARGETS:
        target_name = t['komoditas']
        sup_key = t['supply_raw']
        dem_key = t['demand_raw']
        
        for y in years:
            for p in provinces:
                sup_val = np.nan
                dem_val = np.nan
                
                if sup_key:
                    s = df_supply[(df_supply['tahun'] == y) & (df_supply['provinsi'] == p) & (df_supply['supply_raw'] == sup_key)]
                    if not s.empty:
                        sup_val = s['supply_ton'].sum()
                
                if dem_key:
                    d = df_demand[(df_demand['tahun'] == y) & (df_demand['provinsi'] == p) & (df_demand['demand_raw'] == dem_key)]
                    if not d.empty:
                        dem_val = d['demand_ton'].mean() # mean in case of dupes
                
                has_sup = not pd.isna(sup_val) and sup_val > 0
                has_dem = not pd.isna(dem_val) and dem_val > 0
                
                if not has_sup and not has_dem:
                    continue # Skip fully empty rows
                    
                mode = 'unsupported'
                data_quality = 'poor'
                if has_sup and has_dem:
                    mode = 'full'
                    data_quality = 'high'
                elif has_sup and not has_dem:
                    mode = 'supply_only'
                    data_quality = 'partial_supply'
                elif not has_sup and has_dem:
                    mode = 'demand_only'
                    data_quality = 'partial_demand'
                    
                gap = np.nan
                if mode == 'full':
                    gap = sup_val - dem_val
                    
                fs = True
                if mode == 'unsupported' or mode == 'demand_only':
                    fs = False # no usable supply data
                
                final_rows.append({
                    'tahun': y,
                    'provinsi': p,
                    'komoditas': target_name,
                    'supply_ton': sup_val,
                    'demand_ton': dem_val,
                    'gap_ton': gap,
                    'mapping_type': 'exact',
                    'data_quality': data_quality,
                    'forecast_supported': fs,
                    'optimizer_mode': mode
                })
                
    df_final = pd.DataFrame(final_rows)
    
    # Calculate indexes
    df_final['supply_index'] = df_final.groupby('komoditas')['supply_ton'].transform(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0.5)
    df_final['demand_index'] = df_final.groupby('komoditas')['demand_ton'].transform(lambda x: (x - x.min()) / (x.max() - x.min()) if x.max() > x.min() else 0.5)
    
    df_final.to_csv(OUTPUT_FILE, index=False)
    
    # Generate Report
    with open(REPORT_FILE, 'w') as f:
        f.write("=== DATA QUALITY REPORT ===\n")
        f.write(f"Total Rows: {len(df_final)}\n")
        f.write(f"Unique Provinces: {df_final['provinsi'].nunique()}\n")
        f.write(f"Unique Commodities: {df_final['komoditas'].nunique()}\n")
        f.write("\n=== OPTIMIZER MODE DISTRIBUTION ===\n")
        for mode, count in df_final['optimizer_mode'].value_counts().items():
            f.write(f"{mode}: {count}\n")
        f.write("\n=== DATA QUALITY DISTRIBUTION ===\n")
        for dq, count in df_final['data_quality'].value_counts().items():
            f.write(f"{dq}: {count}\n")
        f.write("\n=== COMMODITY COVERAGE ===\n")
        f.write(df_final.groupby('komoditas')['optimizer_mode'].value_counts().to_string())
        
    print(f"Dataset generated at {OUTPUT_FILE}")
    print(f"Report generated at {REPORT_FILE}")

if __name__ == "__main__":
    main()
