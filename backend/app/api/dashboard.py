from datetime import datetime
import pandas as pd

from fastapi import APIRouter, HTTPException, Request, Response

from app.core.config import settings
from app.services.alert_service import get_sorted_alerts
from app.services.catboost_prediction_service import (
    get_alerts_from_catboost,
    get_all_province_predictions_legacy_contract,
    get_national_statistics_from_catboost,
    get_prediction_legacy_contract,
)
from app.services.dataset_service import (
    get_harga_historis_indexed,
    get_komoditas_objects,
    get_provinsi_objects,
    resolve_komoditas_value,
    resolve_provinsi_value,
)
from app.services.prediction_csv_service import (
    get_all_province_predictions,
    get_daily_forecast,
    get_prediction_summary,
)
from app.services.statistics_service import get_national_statistics
from app.services.runtime_cache_service import cache_get, cache_set
from app.utils.converters import format_date

router = APIRouter()


def _engine(request: Request) -> str:
    return getattr(request.app.state, "prediction_engine", settings.PREDICTION_ENGINE)


def _build_historis_nasional(df_semua, komoditas: str) -> list[dict]:
    if df_semua is None or df_semua.empty:
        return []
    work = df_semua.copy()
    if "jenis_harga" in work.columns:
        work = work[work["jenis_harga"] == "pasar_tradisional"]
    subset = work[work["komoditas"] == komoditas]
    if subset.empty:
        return []
    grouped = (
        subset.groupby("tanggal", as_index=False)["harga"]
        .mean()
        .sort_values("tanggal")
    )
    rows: list[dict] = []
    for _, row in grouped.iterrows():
        t = pd.to_datetime(row.get("tanggal"), errors="coerce")
        if pd.isna(t):
            continue
        rows.append({"tanggal": format_date(t), "harga": float(row.get("harga"))})
    return rows


def _build_prediksi_nasional_from_prediksi_semua(prediksi_semua: list[dict]) -> dict:
    if not prediksi_semua:
        return {"ringkasan": {}, "harian": []}
    def _mean(field: str):
        vals = [float(r.get(field)) for r in prediksi_semua if r.get(field) is not None]
        return (sum(vals) / len(vals)) if vals else None
    harga = _mean("harga_sekarang")
    p7 = _mean("prediksi_7h")
    p30 = _mean("prediksi_30h")
    tren7 = "NAIK" if (p7 is not None and harga is not None and p7 > harga) else ("TURUN" if (p7 is not None and harga is not None and p7 < harga) else "STABIL")
    tren30 = "NAIK" if (p30 is not None and harga is not None and p30 > harga) else ("TURUN" if (p30 is not None and harga is not None and p30 < harga) else "STABIL")
    return {
        "ringkasan": {
            "harga_sekarang": harga,
            "prediksi_7h": p7,
            "prediksi_30h": p30,
            "tren_7h": tren7,
            "tren_30h": tren30,
        },
        "harian": [],
    }


def _build_prediksi_nasional_harian_catboost(app_state, komoditas: str) -> list[dict]:
    service = getattr(app_state, "catboost_prediction_service", None)
    if service is None:
        return []
    df = service.filter_predictions(komoditas=komoditas, jenis_harga="pasar_tradisional")
    if df.empty or "target_date" not in df.columns or "pred_catboost" not in df.columns:
        return []
    grouped = (
        df.groupby("target_date", as_index=False)["pred_catboost"]
        .mean()
        .sort_values("target_date")
    )
    rows: list[dict] = []
    for _, row in grouped.iterrows():
        t = pd.to_datetime(row.get("target_date"), errors="coerce")
        if pd.isna(t):
            continue
        pred = float(row.get("pred_catboost"))
        margin = abs(pred) * 0.03
        rows.append({
            "tanggal": format_date(t),
            "prediksi": pred,
            "batas_bawah": pred - margin,
            "batas_atas": pred + margin,
        })
    return rows


def _build_prediksi_nasional_harian_csv(app_state, komoditas: str) -> list[dict]:
    df_harian = getattr(app_state, "df_harian", None)
    if df_harian is None or df_harian.empty:
        return []
    subset = df_harian[df_harian["komoditas"] == komoditas]
    if subset.empty:
        return []
    grouped = subset.groupby("tanggal", as_index=False).agg(
        {"prediksi": "mean", "batas_bawah": "mean", "batas_atas": "mean"}
    ).sort_values("tanggal")
    rows: list[dict] = []
    for _, row in grouped.iterrows():
        t = pd.to_datetime(row.get("tanggal"), errors="coerce")
        if pd.isna(t):
            continue
        rows.append({
            "tanggal": format_date(t),
            "prediksi": float(row.get("prediksi")),
            "batas_bawah": float(row.get("batas_bawah")),
            "batas_atas": float(row.get("batas_atas")),
        })
    return rows


@router.get("/dashboard/initial")
def get_dashboard_initial(request: Request, response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    cache_key = "dashboard_initial"
    cached = cache_get(request.app.state, cache_key)
    if cached is not None:
        payload = dict(cached)
        metadata = dict(payload.get("metadata", {}))
        metadata["cache"] = "hit"
        payload["metadata"] = metadata
        return payload

    source_df = request.app.state.df_semua
    komoditas = (
        request.app.state.cached_komoditas
        if hasattr(request.app.state, "cached_komoditas")
        and request.app.state.cached_komoditas
        else get_komoditas_objects(source_df)
    )
    provinsi = (
        request.app.state.cached_provinsi
        if hasattr(request.app.state, "cached_provinsi") and request.app.state.cached_provinsi
        else get_provinsi_objects(source_df)
    )

    if _engine(request) == "catboost":
        alert = (
            request.app.state.cached_alerts
            if hasattr(request.app.state, "cached_alerts")
            and request.app.state.cached_alerts is not None
            else get_alerts_from_catboost(request.app.state)
        )
        statistik_nasional = (
            request.app.state.cached_statistik_nasional
            if hasattr(request.app.state, "cached_statistik_nasional")
            and request.app.state.cached_statistik_nasional
            else get_national_statistics_from_catboost(source_df, request.app.state)
        )
    else:
        alert = get_sorted_alerts(request.app.state.alerts)
        statistik_nasional = get_national_statistics(
            request.app.state.df_semua,
            request.app.state.df_hasil,
        )

    default_provinsi = provinsi[0]["slug"] if provinsi else None
    default_komoditas = komoditas[0]["slug"] if komoditas else None
    dataset_max_date = (
        format_date(source_df["tanggal"].max()) if source_df is not None and not source_df.empty else None
    )

    payload = {
        "komoditas": komoditas,
        "provinsi": provinsi,
        "alert": alert,
        "statistik_nasional": statistik_nasional,
        "default_selection": {
            "provinsi": default_provinsi,
            "komoditas": default_komoditas,
        },
        "metadata": {
            "engine": _engine(request),
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "dataset_max_date": dataset_max_date,
            "cache": "miss",
        },
    }
    return cache_set(request.app.state, cache_key, payload, settings.CACHE_TTL_SECONDS)


@router.get("/dashboard/detail")
def get_dashboard_detail(komoditas: str, provinsi: str, request: Request, response: Response):
    response.headers["Cache-Control"] = "public, max-age=120"
    source_df = request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    provinsi_resolved = resolve_provinsi_value(source_df, provinsi)
    if not komoditas_resolved or not provinsi_resolved:
        raise HTTPException(status_code=404, detail="Slug komoditas/provinsi tidak ditemukan")
    cache_key = f"detail::{provinsi_resolved}::{komoditas_resolved}"
    cached = cache_get(request.app.state, cache_key)
    if cached is not None:
        payload = dict(cached)
        metadata = dict(payload.get("metadata", {}))
        metadata["cache"] = "hit"
        payload["metadata"] = metadata
        return payload

    historis = get_harga_historis_indexed(request.app.state, komoditas_resolved, provinsi_resolved)

    if _engine(request) == "catboost":
        prediksi = get_prediction_legacy_contract(
            request.app.state,
            komoditas_resolved,
            provinsi_resolved,
        )
        if hasattr(request.app.state, "cached_prediksi_all") and request.app.state.cached_prediksi_all:
            prediksi_semua = request.app.state.cached_prediksi_all.get(komoditas_resolved)
            if prediksi_semua is None:
                rows = get_all_province_predictions_legacy_contract(
                    request.app.state,
                    komoditas_resolved,
                )
                prediksi_semua = [{**row, "engine": "catboost"} for row in rows]
        else:
            rows = get_all_province_predictions_legacy_contract(
                request.app.state,
                komoditas_resolved,
            )
            prediksi_semua = [{**row, "engine": "catboost"} for row in rows]
        prediksi_nasional_harian = _build_prediksi_nasional_harian_catboost(request.app.state, komoditas_resolved)
    else:
        prediksi = {
            "ringkasan": get_prediction_summary(
                request.app.state.df_hasil,
                komoditas_resolved,
                provinsi_resolved,
            ),
            "harian": get_daily_forecast(
                request.app.state.df_harian,
                komoditas_resolved,
                provinsi_resolved,
            ),
        }
        prediksi_semua = get_all_province_predictions(
            request.app.state.df_hasil,
            komoditas_resolved,
        )
        prediksi_nasional_harian = _build_prediksi_nasional_harian_csv(request.app.state, komoditas_resolved)

    prediksi_nasional = _build_prediksi_nasional_from_prediksi_semua(prediksi_semua)
    prediksi_nasional["harian"] = prediksi_nasional_harian
    historis_nasional = _build_historis_nasional(request.app.state.df_semua, komoditas_resolved)

    payload = {
        "selection": {
            "provinsi": provinsi,
            "komoditas": komoditas,
        },
        "prediksi": prediksi,
        "historis": historis,
        "prediksi_model": prediksi,
        "harga_aktual": historis,
        "prediksi_semua": prediksi_semua,
        "prediksi_nasional": prediksi_nasional,
        "historis_nasional": historis_nasional,
        "recommendation": None,
        "metadata": {
            "engine": _engine(request),
            "prediksi_source": (
                "catboost_h01_h30_full_factor"
                if _engine(request) == "catboost"
                else "csv_fallback"
            ),
            "harga_aktual_source": "harga_historis_2026-01-01_2026-05-20.parquet",
            "cache": "miss",
        },
    }
    return cache_set(request.app.state, cache_key, payload, settings.CACHE_TTL_SECONDS)
