import pandas as pd
import numpy as np

df = pd.read_csv(r'd:\2026\pangan-ai\panganai\backend\data\master_supply_demand.csv')

print("=== CHECK 1: YEAR DISTRIBUTION ===")
print(df['tahun'].value_counts().sort_index().to_string())

print("\n=== CHECK 2: LATEST AVAILABLE YEAR ===")
for kom in df['komoditas'].unique():
    subset = df[df['komoditas'] == kom]
    sup_years = subset[subset['supply_ton'].notna()]['tahun']
    dem_years = subset[subset['demand_ton'].notna()]['tahun']
    
    latest_sup = int(sup_years.max()) if len(sup_years) > 0 else 'None'
    latest_dem = int(dem_years.max()) if len(dem_years) > 0 else 'None'
    print(f"{kom}: Supply={latest_sup}, Demand={latest_dem}")

print("\n=== CHECK 4: 2025 COVERAGE ===")
df_2025 = df[df['tahun'] == 2025]
for kom in df['komoditas'].unique():
    subset = df_2025[df_2025['komoditas'] == kom]
    if len(subset) > 0:
        mode_counts = subset['optimizer_mode'].value_counts().to_dict()
        print(f"{kom}: {len(subset)} provinces, modes={mode_counts}")
    else:
        print(f"{kom}: NO DATA FOR 2025")

print("\n=== CHECK 5: ROUTING FEASIBILITY (2025) ===")
for kom in df['komoditas'].unique():
    subset = df_2025[df_2025['komoditas'] == kom]
    surplus = subset[subset['gap_ton'] > 0]
    deficit = subset[subset['gap_ton'] < 0]
    print(f"{kom}: Surplus Provs={len(surplus)}, Deficit Provs={len(deficit)}")
