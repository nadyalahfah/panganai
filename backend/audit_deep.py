import os
import pandas as pd

directory = r"d:\2026\pangan-ai\panganai\backend\data\raw_supply_demand\raw_supply_demand"
files = [f for f in os.listdir(directory) if f.endswith('.csv') or f.endswith('.xlsx')]

# Filter to demand files (consumption, skor, rasio)
demand_files = [f for f in files if "Konsumsi" in f or "Kecukupan" in f or "Pola" in f]

search_terms = ['cabai', 'bawang', 'chili', 'onion', 'shallot', 'merah', 'keriting', 'rawit']

results = []

def search_df(df, filename, sheet_name=""):
    # Check columns
    for col in df.columns:
        col_str = str(col).lower()
        if any(term in col_str for term in search_terms):
            results.append(f"FOUND IN COLUMN: {col} | FILE: {filename} | SHEET: {sheet_name}")
    
    # Check all object/string columns for values
    for col in df.select_dtypes(include=['object', 'string']).columns:
        unique_vals = df[col].dropna().astype(str).unique()
        for val in unique_vals:
            val_lower = val.lower()
            if any(term in val_lower for term in search_terms):
                results.append(f"FOUND IN VALUE: '{val}' (Column: {col}) | FILE: {filename} | SHEET: {sheet_name}")

for file in demand_files:
    file_path = os.path.join(directory, file)
    try:
        if file.endswith('.csv'):
            df = pd.read_csv(file_path, sep=None, engine='python')
            search_df(df, file)
        elif file.endswith('.xlsx'):
            xls = pd.ExcelFile(file_path)
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet)
                search_df(df, file, sheet_name=sheet)
    except Exception as e:
        results.append(f"ERROR reading {file}: {e}")

print("=== DEEP AUDIT RESULTS ===")
if not results:
    print("NO SPECIFIC MATCHES FOR CABAI/BAWANG FOUND IN DEMAND DATASETS.")
else:
    for r in sorted(list(set(results))):
        print(r)
