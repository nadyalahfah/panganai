import pandas as pd

from app.core.config import settings


def resolve_main_dataset_path():
    if settings.DATASET_FEATURE_ENGINEERED_PATH.exists():
        return settings.DATASET_FEATURE_ENGINEERED_PATH
    raise FileNotFoundError(
        f"Main dataset tidak ditemukan: {settings.DATASET_FEATURE_ENGINEERED_PATH}"
    )


def load_main_dataset() -> pd.DataFrame:
    dataset_path = resolve_main_dataset_path()
    df = pd.read_csv(dataset_path, low_memory=False)
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df
