import pandas as pd

from app.core.config import settings


def load_prediction_summary() -> pd.DataFrame:
    df = pd.read_csv(settings.PREDICTIONS_CSV_DIR / "hasil_prediksi.csv")
    df["tanggal_data"] = pd.to_datetime(df["tanggal_data"])
    return df


def load_daily_prediction() -> pd.DataFrame:
    df = pd.read_csv(settings.PREDICTIONS_CSV_DIR / "prediksi_harian.csv")
    df["tanggal"] = pd.to_datetime(df["tanggal"])
    return df
