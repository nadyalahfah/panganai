import pandas as pd

from app.core.config import settings


def resolve_main_dataset_path():
    if settings.DATASET_SEMUA_PATH.exists():
        return settings.DATASET_SEMUA_PATH
    if settings.DATASET_FEATURE_ENGINEERED_PATH.exists():
        return settings.DATASET_FEATURE_ENGINEERED_PATH
    raise FileNotFoundError(
        f"Main dataset tidak ditemukan: {settings.DATASET_SEMUA_PATH} atau {settings.DATASET_FEATURE_ENGINEERED_PATH}"
    )


def load_main_dataset() -> pd.DataFrame:
    dataset_path = resolve_main_dataset_path()
    
    # Baca header dulu untuk cek kolom yang ada
    columns = pd.read_csv(dataset_path, nrows=0).columns.tolist()
    keep_cols = {"tanggal", "provinsi", "komoditas", "harga", "satuan", "jenis_harga", "level_harga", "sumber_harga"}
    use_cols = [c for c in columns if c in keep_cols]
    
    chunks = []
    for chunk in pd.read_csv(dataset_path, usecols=use_cols, chunksize=100000, low_memory=False):
        chunks.append(chunk)
        
    if not chunks:
        df = pd.DataFrame(columns=use_cols)
    else:
        df = pd.concat(chunks, ignore_index=True)
    
    required_columns = ["tanggal", "provinsi", "komoditas", "harga"]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise RuntimeError(f"Kolom wajib tidak ditemukan di {dataset_path.name}: {missing_cols}")
        
    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df
