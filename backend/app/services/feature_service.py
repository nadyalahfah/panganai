from pathlib import Path
import re

import pandas as pd
from fastapi import HTTPException

from app.core.config import settings

DATASET_FEATURE_PATHS = [
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


def load_feature_dataset() -> pd.DataFrame:
    path = _resolve_feature_dataset_path()
    df = pd.read_csv(path, low_memory=False)
    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df


def _normalize_text(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()
    return re.sub(r"\s+", " ", value)


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
