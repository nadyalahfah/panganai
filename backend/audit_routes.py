import pandas as pd
import sys
import os

print("--- OPTIMIZER ENGINE TRACE ---")

try:
    df_semua = pd.read_csv('data/master_supply_demand.csv')
    print(f"1. Total rows loaded from CSV: {len(df_semua)}")
    
    # 1. Filter mapping type
    df_current = df_semua[df_semua['mapping_type'].fillna('').str.lower() != 'unsupported']
    print(f"2. Rows after mapping_type != unsupported: {len(df_current)}")
    
    # 2. Latest year
    if 'tahun' in df_current.columns:
        latest_year = df_current['tahun'].max()
        print(f"3. Latest year selected: {latest_year}")
        df_current = df_current[df_current['tahun'] == latest_year]
        print(f"4. Rows surviving latest year filter: {len(df_current)}")
    else:
        print("3. No 'tahun' column found")
        
    # 3. Mode filter (which I added previously)
    df_full = df_current[df_current['optimizer_mode'].fillna('FULL').str.lower() == 'full']
    print(f"5. Rows after optimizer_mode == 'full': {len(df_full)}")

    if len(df_full) == 0:
        print("-> ROOT CAUSE: No rows matched optimizer_mode == 'full' for the latest year!")
        
        # Let's see what modes exist for the latest year
        print("-> Modes available in latest year:")
        print(df_current['optimizer_mode'].value_counts(dropna=False))
except Exception as e:
    print(f"Error reading CSV: {e}")
