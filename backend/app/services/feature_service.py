from pathlib import Path
import re

import pandas as pd
from fastapi import HTTPException

from app.core.config import settings

DATASET_FEATURE_PATHS = [
    settings.DATASET_FEATURE_ENGINEERED_PATH,
    settings.DATA_DIR / "dataset" / "data_to_train" / "final_training_dataset_feature_engineered.csv",
    settings.DATA_DIR / "dataset" / "final_training_dataset_feature_engineered.csv",
]


def _resolve_feature_dataset_path() -> Path:
    for candidate in DATASET_FEATURE_PATHS:
        if candidate.exists():
            return candidate
    raise FileNotFoundError(
        f"Feature-engineered dataset tidak ditemukan. Checked: {[str(p) for p in DATASET_FEATURE_PATHS]}"
    )


def load_feature_dataset(feature_cols: list[str]) -> pd.DataFrame:
    path = _resolve_feature_dataset_path()
    
    # Read in chunks to avoid OOM on 446MB file
    chunks = []
    group_cols = ["provinsi", "komoditas"]
    first_chunk = True
    
    # 1. Inspect first row to ensure columns exist
    available_cols = set(pd.read_csv(path, nrows=0).columns)
    base_cols = ["tanggal", "provinsi", "komoditas", "jenis_harga", "level_harga"]
    required_cols = list(set([c for c in base_cols if c in available_cols] + feature_cols))
    
    missing = [c for c in required_cols if c not in available_cols]
    if missing:
        raise RuntimeError(f"Kolom wajib tidak ditemukan di dataset fitur: {missing}")
    
    total_rows_processed = 0
    for chunk in pd.read_csv(path, usecols=required_cols, chunksize=50000, low_memory=False):
        total_rows_processed += len(chunk)
        if "tanggal" in chunk.columns:
            chunk["tanggal"] = pd.to_datetime(chunk["tanggal"])
            
        if first_chunk:
            if "jenis_harga" in chunk.columns:
                group_cols.append("jenis_harga")
            if "level_harga" in chunk.columns:
                group_cols.append("level_harga")
            first_chunk = False
            
        idx = chunk.groupby(group_cols, dropna=False)["tanggal"].idxmax()
        chunks.append(chunk.loc[idx])
        
    if not chunks:
        return pd.DataFrame()
        
    combined = pd.concat(chunks, ignore_index=True)
    final_idx = combined.groupby(group_cols, dropna=False)["tanggal"].idxmax()
    final_df = combined.loc[final_idx].copy()
    
    import logging
    logger = logging.getLogger("panganai")
    logger.info(f"Feature dataset processed: {total_rows_processed:,} rows. Retained: {len(final_df):,} rows.")
    logger.info(f"Columns loaded: {len(required_cols)}")
    
    return final_df


def _normalize_text(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    return re.sub(r"\s+", " ", value)


def _optional_norm(value):
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return _normalize_text(value)


def build_latest_features_index(df: pd.DataFrame):
    if df is None or df.empty:
        return {}
    index = {}
    for _, row in df.iterrows():
        key = (
            _normalize_text(row.get("provinsi", "")),
            _normalize_text(row.get("komoditas", "")),
            _optional_norm(row.get("jenis_harga")),
            _optional_norm(row.get("level_harga")),
        )
        index[key] = row
    return index


def get_latest_row_from_index(
    feature_index: dict,
    provinsi: str,
    komoditas: str,
    jenis_harga: str | None = None,
    level_harga: str | None = None,
):
    if not feature_index:
        return None
    base_key = (
        _normalize_text(provinsi),
        _normalize_text(komoditas),
        _optional_norm(jenis_harga),
        _optional_norm(level_harga),
    )
    row = feature_index.get(base_key)
    if row is not None:
        return row
    fallback_key = (
        _normalize_text(provinsi),
        _normalize_text(komoditas),
        "",
        "",
    )
    return feature_index.get(fallback_key)


def _match_commodity(df: pd.DataFrame, komoditas: str) -> str | None:
    exact = df[df["komoditas"] == komoditas]
    if not exact.empty:
        return komoditas

    aliases = {
        "beras medium i": "beras kualitas medium i",
    }
    norm_target = _normalize_text(komoditas)
    alias_target = aliases.get(norm_target, norm_target)

    unique_vals = df["komoditas"].dropna().astype(str).unique().tolist()
    for val in unique_vals:
        if _normalize_text(val) == alias_target:
            return val
    return None


def get_latest_row(
    df: pd.DataFrame,
    provinsi: str,
    komoditas: str,
    jenis_harga: str | None = None,
    level_harga: str | None = None,
) -> pd.Series:
    matched_commodity = _match_commodity(df, komoditas)
    if matched_commodity is None:
        raise HTTPException(status_code=404, detail="Data fitur untuk filter yang diminta tidak ditemukan")

    mask = (df["komoditas"] == matched_commodity) & (df["provinsi"] == provinsi)
    if jenis_harga is not None and "jenis_harga" in df.columns:
        mask = mask & (df["jenis_harga"] == jenis_harga)
    if level_harga is not None and "level_harga" in df.columns:
        mask = mask & (df["level_harga"] == level_harga)

    subset = df[mask].sort_values("tanggal")
    if subset.empty:
        raise HTTPException(status_code=404, detail="Data fitur untuk filter yang diminta tidak ditemukan")
    return subset.iloc[-1]


def validate_required_features(row: pd.Series, feature_columns: list[str]):
    missing = [col for col in feature_columns if col not in row.index]
    if missing:
        raise HTTPException(status_code=500, detail=f"Missing model features: {missing}")


def build_prediction_matrix(row: pd.Series, feature_columns: list[str]) -> pd.DataFrame:
    validate_required_features(row, feature_columns)
    x = pd.DataFrame([[row[col] for col in feature_columns]], columns=feature_columns)
    return x
