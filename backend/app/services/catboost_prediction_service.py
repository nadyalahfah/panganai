import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd
from catboost import CatBoostRegressor
from catboost import Pool

from app.utils.converters import safe_float
from app.core.config import settings

logger = logging.getLogger("panganai")


class CatBoostPredictionService:
    EXCLUDE_COLUMNS = {
        "prediction_date",
        "target_date",
        "provinsi",
        "komoditas",
        "jenis_harga",
        "level_harga",
        "harga_terakhir",
        "harga",
        "pred_catboost",
        "pred_naive",
        "actual",
        "target_harga",
        "harga_target_h7",
    }

    META_COLUMNS = [
        "prediction_date",
        "target_date",
        "horizon_days",
        "provinsi",
        "komoditas",
        "jenis_harga",
        "level_harga",
        "harga_terakhir",
    ]

    def __init__(self, model_path: str | Path, input_parquet_path: str | Path, manifest_path: str | Path | None = None):
        self.model_path = Path(model_path)
        self.input_parquet_path = Path(input_parquet_path)
        self.manifest_path = Path(manifest_path) if manifest_path else None
        self.model: CatBoostRegressor | None = None
        self.input_df: pd.DataFrame | None = None
        self.pred_df: pd.DataFrame | None = None
        self.feature_columns: list[str] = []
        self.cat_feature_indices: list[int] = []
        self.cat_feature_columns: list[str] = []
        self.status: dict[str, Any] = {
            "available": False,
            "loaded": False,
            "predicted": False,
            "error": None,
            "model_path": str(self.model_path),
            "input_path": str(self.input_parquet_path),
            "rows": 0,
            "prediction_rows": 0,
            "target_date_min": None,
            "target_date_max": None,
        }

    def _load_manifest_features(self) -> list[str] | None:
        candidate_paths: list[Path] = []
        if self.manifest_path:
            candidate_paths.append(self.manifest_path)
            if not self.manifest_path.is_absolute():
                candidate_paths.append(Path.cwd() / self.manifest_path)

        manifest_file = next((p for p in candidate_paths if p.exists()), None)
        if manifest_file is None:
            logger.warning("Model manifest not found at %s. Falling back to inferred feature columns.", self.manifest_path)
            return None

        try:
            data = json.loads(manifest_file.read_text(encoding="utf-8"))
        except Exception as exc:
            logger.warning("Failed reading manifest JSON (%s): %s", manifest_file, exc)
            return None

        for key in ("feature_columns", "features", "model_features"):
            cols = data.get(key)
            if isinstance(cols, list) and cols:
                return [str(c) for c in cols]

        logger.warning("Manifest loaded but no feature_columns key found at %s", manifest_file)
        return None

    def _infer_feature_columns(self, df: pd.DataFrame) -> list[str]:
        cols: list[str] = []
        for col in df.columns:
            if col in self.EXCLUDE_COLUMNS or col.startswith("harga_target"):
                continue
            cols.append(col)
        return cols

    def _coerce_feature_types(self, df: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
        x = df[feature_columns].copy()
        cat_cols = set(self.cat_feature_columns)
        for col in feature_columns:
            # CatBoost requires categorical features as string/integer IDs; float is invalid.
            if col in cat_cols:
                x[col] = x[col].astype("string").fillna("unknown")
                continue

            if pd.api.types.is_datetime64_any_dtype(x[col]):
                x[col] = pd.to_datetime(x[col], errors="coerce").astype("int64") // 10**9
            else:
                # For non-categorical features we always coerce to numeric.
                x[col] = pd.to_numeric(x[col], errors="coerce")

        for col in x.columns:
            if col in cat_cols:
                x[col] = x[col].astype("string").fillna("unknown")
            elif not (pd.api.types.is_object_dtype(x[col]) or pd.api.types.is_string_dtype(x[col])):
                med = x[col].median()
                x[col] = x[col].fillna(0 if pd.isna(med) else med)
            else:
                x[col] = x[col].fillna("unknown")
        return x

    def load(self) -> None:
        self.status.update({"available": False, "loaded": False, "predicted": False, "error": None})
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            if not self.input_parquet_path.exists():
                raise FileNotFoundError(f"Model input parquet not found: {self.input_parquet_path}")

            self.model = CatBoostRegressor()
            self.model.load_model(str(self.model_path))

            self.input_df = pd.read_parquet(self.input_parquet_path)
            if "harga_terakhir" not in self.input_df.columns and "harga" in self.input_df.columns:
                self.input_df["harga_terakhir"] = self.input_df["harga"]

            model_features = [str(c) for c in (self.model.feature_names_ or [])]
            if model_features:
                missing = [c for c in model_features if c not in self.input_df.columns]
                if missing:
                    raise RuntimeError(f"Model feature columns missing from input parquet: {missing[:20]}")
                self.feature_columns = model_features
            else:
                manifest_features = self._load_manifest_features()
                if manifest_features:
                    missing = [c for c in manifest_features if c not in self.input_df.columns]
                    if missing:
                        raise RuntimeError(f"Manifest feature columns missing from input parquet: {missing[:20]}")
                    self.feature_columns = manifest_features
                else:
                    self.feature_columns = self._infer_feature_columns(self.input_df)

            self.cat_feature_indices = list(self.model.get_cat_feature_indices() or [])
            self.cat_feature_columns = [
                self.feature_columns[i]
                for i in self.cat_feature_indices
                if 0 <= i < len(self.feature_columns)
            ]

            self.status.update(
                {
                    "available": True,
                    "loaded": True,
                    "rows": int(len(self.input_df)),
                    "columns": int(len(self.input_df.columns)),
                    "feature_count": len(self.feature_columns),
                    "cat_feature_count": len(self.cat_feature_columns),
                }
            )
            logger.info("Model input loaded: rows=%s cols=%s", len(self.input_df), len(self.input_df.columns))
        except Exception as exc:
            self.status["error"] = str(exc)
            logger.exception("Failed loading CatBoost prediction service: %s", exc)

    def predict_all(self) -> None:
        if not self.status.get("loaded") or self.input_df is None or self.model is None:
            self.status["error"] = self.status.get("error") or "Service not loaded"
            return

        try:
            x = self._coerce_feature_types(self.input_df, self.feature_columns)
            pool = Pool(data=x, cat_features=self.cat_feature_indices)
            preds = self.model.predict(pool)

            pred_df = self.input_df.copy()
            pred_df["pred_catboost"] = preds
            if "pred_naive" not in pred_df.columns:
                if "harga_terakhir" in pred_df.columns:
                    pred_df["pred_naive"] = pred_df["harga_terakhir"]
                elif "harga" in pred_df.columns:
                    pred_df["pred_naive"] = pred_df["harga"]
                else:
                    pred_df["pred_naive"] = None

            if "prediction_date" not in pred_df.columns:
                pred_df["prediction_date"] = pd.Timestamp.utcnow().normalize()

            if "horizon_days" not in pred_df.columns and "target_date" in pred_df.columns and "prediction_date" in pred_df.columns:
                td = pd.to_datetime(pred_df["target_date"], errors="coerce")
                pdte = pd.to_datetime(pred_df["prediction_date"], errors="coerce")
                pred_df["horizon_days"] = (td - pdte).dt.days

            self.pred_df = pred_df
            target_min = None
            target_max = None
            if "target_date" in pred_df.columns:
                td = pd.to_datetime(pred_df["target_date"], errors="coerce")
                if not td.empty:
                    target_min = td.min()
                    target_max = td.max()

            self.status.update(
                {
                    "predicted": True,
                    "prediction_rows": int(len(pred_df)),
                    "target_date_min": target_min.isoformat() if pd.notna(target_min) else None,
                    "target_date_max": target_max.isoformat() if pd.notna(target_max) else None,
                }
            )
            logger.info(
                "Prediction ready: rows=%s target_range=%s..%s",
                len(pred_df),
                self.status["target_date_min"],
                self.status["target_date_max"],
            )
        except Exception as exc:
            self.status["error"] = str(exc)
            logger.exception("CatBoost predict failed: %s", exc)

    def get_predictions(self) -> pd.DataFrame:
        return self.pred_df.copy() if self.pred_df is not None else pd.DataFrame()

    def filter_predictions(self, provinsi=None, komoditas=None, jenis_harga=None, level_harga=None) -> pd.DataFrame:
        df = self.get_predictions()
        if df.empty:
            return df
        if provinsi is not None and "provinsi" in df.columns:
            df = df[df["provinsi"] == provinsi]
        if komoditas is not None and "komoditas" in df.columns:
            df = df[df["komoditas"] == komoditas]
        if jenis_harga is not None and "jenis_harga" in df.columns:
            df = df[df["jenis_harga"] == jenis_harga]
        if level_harga is not None and "level_harga" in df.columns:
            df = df[df["level_harga"] == level_harga]
        return df

    def get_status(self) -> dict[str, Any]:
        return dict(self.status)


def _trend_label(pred, current):
    if pred > current:
        return "NAIK"
    if pred < current:
        return "TURUN"
    return "STABIL"


def _build_harian(subset: pd.DataFrame) -> list[dict[str, Any]]:
    if subset.empty:
        return []

    rows = []
    work = subset.copy()
    if "target_date" in work.columns:
        work = work.sort_values("target_date")

    for _, row in work.iterrows():
        target = pd.to_datetime(row.get("target_date"), errors="coerce")
        pred = safe_float(row.get("pred_catboost"))
        if pred is None:
            continue
        margin = abs(pred) * 0.03
        rows.append(
            {
                "tanggal": target.strftime("%Y-%m-%d") if pd.notna(target) else None,
                "prediksi": pred,
                "batas_bawah": safe_float(pred - margin),
                "batas_atas": safe_float(pred + margin),
            }
        )
    return rows


def _pick_horizon_pred(subset: pd.DataFrame, horizon: int, fallback_idx: int) -> float | None:
    if subset.empty:
        return None
    if "horizon_days" in subset.columns:
        matched = subset[subset["horizon_days"] == horizon]
        if not matched.empty:
            return safe_float(matched.iloc[0].get("pred_catboost"))
    idx = min(max(fallback_idx, 0), len(subset) - 1)
    return safe_float(subset.iloc[idx].get("pred_catboost"))


def predict_single(df, model, feature_columns, provinsi, komoditas, jenis_harga=None, level_harga=None, horizon=30):
    # New path: use precomputed predictions from CatBoostPredictionService when available.
    service = getattr(model, "_service_ref", None)
    if service is None:
        raise RuntimeError("CatBoostPredictionService reference not found for predict_single")

    subset = service.filter_predictions(
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    )
    if subset.empty:
        raise ValueError("Data prediksi tidak ditemukan untuk kombinasi provinsi/komoditas")

    if "horizon_days" in subset.columns:
        subset = subset[subset["horizon_days"].between(1, horizon)]

    subset = subset.sort_values("target_date") if "target_date" in subset.columns else subset
    first = subset.iloc[0]

    harga_sekarang = safe_float(first.get("harga_terakhir") if "harga_terakhir" in first else first.get("harga"))
    pred_7 = _pick_horizon_pred(subset, 7, 6)
    pred_30 = _pick_horizon_pred(subset, 30, len(subset) - 1)

    tren_7h = _trend_label(pred_7 or 0, harga_sekarang or 0)
    tren_30h = _trend_label(pred_30 or 0, harga_sekarang or 0)
    mae = abs((pred_7 or 0) * 0.03)

    return {
        "provinsi": provinsi,
        "komoditas": komoditas,
        "harga_sekarang": harga_sekarang,
        "last_data_date": None,
        "target_date_7h": None,
        "prediksi_7h": pred_7,
        "prediksi_30h": pred_30,
        "tren_7h": tren_7h,
        "tren_30h": tren_30h,
        "prototype_recursive_forecast": False,
        "forecast_30h_source": "native_h01_h30",
        "note": "Prediksi berasal dari model input horizon H+1..H+30.",
        "bawah_7h": safe_float((pred_7 or 0) - mae),
        "atas_7h": safe_float((pred_7 or 0) + mae),
        "bawah_30h": safe_float((pred_30 or 0) - (mae * 2)),
        "atas_30h": safe_float((pred_30 or 0) + (mae * 2)),
        "mape_pct": safe_float((mae / abs(harga_sekarang) * 100) if harga_sekarang else 0),
        "mae": safe_float(mae),
        "harian": _build_harian(subset),
    }


def get_prediction_legacy_contract(app_state, komoditas, provinsi):
    result = predict_single(
        df=None,
        model=app_state.model,
        feature_columns=app_state.feature_columns,
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga="pasar_tradisional",
        horizon=30,
    )
    return {"ringkasan": {
        "harga_sekarang": result["harga_sekarang"],
        "prediksi_7h": result["prediksi_7h"],
        "prediksi_30h": result["prediksi_30h"],
        "tren_7h": result["tren_7h"],
        "tren_30h": result["tren_30h"],
        "mape_pct": result["mape_pct"],
        "bawah_7h": result["bawah_7h"],
        "atas_7h": result["atas_7h"],
        "bawah_30h": result["bawah_30h"],
        "atas_30h": result["atas_30h"],
        "mae": result["mae"],
    }, "harian": result["harian"]}


def get_all_province_predictions_legacy_contract(app_state, komoditas):
    service = getattr(app_state, "catboost_prediction_service", None)
    if service is None:
        return []
    subset = service.filter_predictions(komoditas=komoditas, jenis_harga="pasar_tradisional")
    if subset.empty:
        return []

    rows = []
    for provinsi in sorted(subset["provinsi"].dropna().unique().tolist()):
        p = subset[subset["provinsi"] == provinsi].sort_values("target_date")
        if p.empty:
            continue
        base = safe_float(p.iloc[0].get("harga_terakhir") if "harga_terakhir" in p.columns else p.iloc[0].get("harga"))
        pred1 = _pick_horizon_pred(p, 1, 0)
        pred7 = _pick_horizon_pred(p, 7, 6)
        pred30 = _pick_horizon_pred(p, 30, len(p) - 1)
        rows.append(
            {
                "provinsi": provinsi,
                "harga_sekarang": base,
                "prediksi_1h": pred1,
                "prediksi_7h": pred7,
                "prediksi_30h": pred30,
                "tren_7h": _trend_label(pred7 or 0, base or 0),
                "tren_30h": _trend_label(pred30 or 0, base or 0),
                "ubah_1_pct": round(((pred1 - base) / base) * 100, 1) if base and pred1 else 0,
                "ubah_7_pct": round(((pred7 - base) / base) * 100, 1) if base and pred7 else 0,
                "ubah_30_pct": round(((pred30 - base) / base) * 100, 1) if base and pred30 else 0,
            }
        )
    return rows


def get_alerts_from_catboost(app_state, kenaikan_min_pct=5.0):
    def _risk_level(pct: float) -> str:
        ap = abs(pct)
        if ap >= 20:
            return "CRITICAL"
        if ap >= 10:
            return "HIGH"
        if ap >= 5:
            return "WATCH"
        return "LOW"

    def _reasoning(provinsi: str, komoditas: str, base: float, pred7: float, pred30: float | None, pct7: float) -> str:
        arah = "naik" if pct7 > 0 else ("turun" if pct7 < 0 else "stabil")
        level = _risk_level(pct7)
        if level == "CRITICAL":
            awalan = "Perubahan harga sangat tajam dan berisiko mengganggu stabilitas pasokan."
        elif level == "HIGH":
            awalan = "Pergerakan harga cukup tinggi dan perlu pengawasan intensif."
        elif level == "WATCH":
            awalan = "Terlihat gejolak harga awal yang perlu dipantau agar tidak bereskalasi."
        else:
            awalan = "Perubahan harga masih relatif terkendali."
        return (
            f"{awalan} Di {provinsi}, {komoditas} diproyeksikan {arah} "
            f"{abs(pct7):.1f}% dalam 7 hari (dari Rp{base:,.0f} ke Rp{pred7:,.0f}). "
            f"Proyeksi 30 hari berada di sekitar Rp{(pred30 or pred7):,.0f}."
        ).replace(",", ".")

    kenaikan_min_pct = float(getattr(settings, "ALERT_MIN_CHANGE_PCT", kenaikan_min_pct))
    alerts = []
    service = getattr(app_state, "catboost_prediction_service", None)
    if service is None:
        return []

    df = service.get_predictions()
    if df.empty:
        return []

    for (provinsi, komoditas), grp in df.groupby(["provinsi", "komoditas"]):
        g = grp.sort_values("target_date")
        base = safe_float(g.iloc[0].get("harga_terakhir") if "harga_terakhir" in g.columns else g.iloc[0].get("harga"))
        pred7 = _pick_horizon_pred(g, 7, 6)
        pred30 = _pick_horizon_pred(g, 30, len(g) - 1)
        if base is None or pred7 is None:
            continue
        kenaikan_pct = round(((pred7 - base) / base) * 100, 1) if base else 0
        if abs(kenaikan_pct) < kenaikan_min_pct:
            continue
        ubah_30_pct = round(((pred30 - base) / base) * 100, 1) if (base and pred30 is not None) else 0
        risk_level = _risk_level(kenaikan_pct)
        alerts.append({
            "provinsi": provinsi,
            "komoditas": komoditas,
            "harga_sekarang": base,
            "prediksi_7h": pred7,
            "prediksi_30h": pred30,
            "kenaikan_pct": kenaikan_pct,
            "ubah_30_pct": ubah_30_pct,
            "risk_level": risk_level,
            "ai_reasoning": _reasoning(provinsi, komoditas, base, pred7, pred30, kenaikan_pct),
            "engine": "catboost",
        })
    return sorted(alerts, key=lambda x: abs(x.get("kenaikan_pct", 0)), reverse=True)


def get_national_statistics_from_catboost(df_semua, app_state):
    service = getattr(app_state, "catboost_prediction_service", None)
    if service is None:
        return []

    pred_df = service.get_predictions()
    if pred_df.empty:
        return []

    result = []
    for komoditas in sorted(pred_df["komoditas"].dropna().unique().tolist()):
        pred_all = get_all_province_predictions_legacy_contract(app_state, komoditas)
        if not pred_all:
            continue
        tren_counts = {}
        for row in pred_all:
            tren = row.get("tren_30h", "STABIL")
            tren_counts[tren] = tren_counts.get(tren, 0) + 1
        tren_mayoritas = max(tren_counts, key=tren_counts.get)

        today_subset = df_semua[df_semua["komoditas"] == komoditas] if df_semua is not None and not df_semua.empty else pd.DataFrame()
        if not today_subset.empty and "tanggal" in today_subset.columns:
            latest_date = today_subset["tanggal"].max()
            today_subset = today_subset[today_subset["tanggal"] == latest_date]
        harga_avg = safe_float(today_subset["harga"].mean()) if (not today_subset.empty and "harga" in today_subset.columns) else None

        result.append({
            "komoditas": komoditas,
            "harga_rata_nasional": harga_avg,
            "tren_30h_mayoritas": tren_mayoritas,
            "engine": "catboost",
        })
    return result
