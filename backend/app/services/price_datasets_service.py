import logging
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger("panganai")


class PriceDatasetsService:
    def __init__(self, historical_parquet_path: str | Path, historical_csv_fallback_path: str | Path | None = None, summary_parquet_path: str | Path | None = None):
        self.historical_parquet_path = Path(historical_parquet_path)
        self.historical_csv_fallback_path = Path(historical_csv_fallback_path) if historical_csv_fallback_path else None
        self.summary_parquet_path = Path(summary_parquet_path) if summary_parquet_path else None
        self.history_df: pd.DataFrame | None = None
        self.summary_df: pd.DataFrame | None = None
        self.status: dict[str, Any] = {
            "loaded": False,
            "history_rows": 0,
            "summary_rows": 0,
            "history_date_min": None,
            "history_date_max": None,
            "error": None,
            "history_source": None,
        }

    def load(self) -> None:
        self.status.update({"loaded": False, "error": None})
        try:
            if self.historical_parquet_path.exists():
                self.history_df = pd.read_parquet(self.historical_parquet_path)
                self.status["history_source"] = str(self.historical_parquet_path)
            elif self.historical_csv_fallback_path and self.historical_csv_fallback_path.exists():
                self.history_df = pd.read_csv(self.historical_csv_fallback_path)
                self.status["history_source"] = str(self.historical_csv_fallback_path)
            else:
                raise FileNotFoundError("Historical parquet/csv source is missing")

            if "tanggal" in self.history_df.columns:
                self.history_df["tanggal"] = pd.to_datetime(self.history_df["tanggal"], errors="coerce")

            if self.summary_parquet_path and self.summary_parquet_path.exists():
                self.summary_df = pd.read_parquet(self.summary_parquet_path)
                if "tanggal" in self.summary_df.columns:
                    self.summary_df["tanggal"] = pd.to_datetime(self.summary_df["tanggal"], errors="coerce")
            else:
                self.summary_df = pd.DataFrame()

            hmin = self.history_df["tanggal"].min() if "tanggal" in self.history_df.columns and not self.history_df.empty else None
            hmax = self.history_df["tanggal"].max() if "tanggal" in self.history_df.columns and not self.history_df.empty else None
            self.status.update(
                {
                    "loaded": True,
                    "history_rows": int(len(self.history_df)),
                    "summary_rows": int(len(self.summary_df)) if self.summary_df is not None else 0,
                    "history_date_min": hmin.isoformat() if pd.notna(hmin) else None,
                    "history_date_max": hmax.isoformat() if pd.notna(hmax) else None,
                }
            )
        except Exception as exc:
            self.status["error"] = str(exc)
            logger.exception("Failed loading price datasets: %s", exc)

    def _filter(self, df: pd.DataFrame, provinsi=None, komoditas=None, jenis_harga=None, level_harga=None) -> pd.DataFrame:
        out = df.copy()
        if out.empty:
            return out
        if provinsi is not None and "provinsi" in out.columns:
            out = out[out["provinsi"] == provinsi]
        if komoditas is not None and "komoditas" in out.columns:
            out = out[out["komoditas"] == komoditas]
        if jenis_harga is not None and "jenis_harga" in out.columns:
            out = out[out["jenis_harga"] == jenis_harga]
        if level_harga is not None and "level_harga" in out.columns:
            out = out[out["level_harga"] == level_harga]
        return out

    def get_history(self, provinsi=None, komoditas=None, jenis_harga=None, level_harga=None) -> list[dict[str, Any]]:
        df = self._filter(self.history_df.copy() if self.history_df is not None else pd.DataFrame(), provinsi, komoditas, jenis_harga, level_harga)
        if "tanggal" in df.columns:
            df = df.sort_values("tanggal")
            df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")
        return df.to_dict(orient="records")

    def get_summary(self, provinsi=None, komoditas=None, jenis_harga=None, level_harga=None) -> list[dict[str, Any]]:
        df = self._filter(self.summary_df.copy() if self.summary_df is not None else pd.DataFrame(), provinsi, komoditas, jenis_harga, level_harga)
        if "tanggal" in df.columns:
            df = df.sort_values("tanggal")
            df["tanggal"] = df["tanggal"].dt.strftime("%Y-%m-%d")
        return df.to_dict(orient="records")

    def get_chart_data(self, provinsi=None, komoditas=None, jenis_harga=None, level_harga=None) -> dict[str, Any]:
        return {
            "history": self.get_history(provinsi, komoditas, jenis_harga, level_harga),
            "summary": self.get_summary(provinsi, komoditas, jenis_harga, level_harga),
        }

    def get_status(self) -> dict[str, Any]:
        return dict(self.status)
