from datetime import datetime

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

    payload = {
        "selection": {
            "provinsi": provinsi,
            "komoditas": komoditas,
        },
        "prediksi": prediksi,
        "historis": historis,
        "prediksi_semua": prediksi_semua,
        "recommendation": None,
        "metadata": {
            "engine": _engine(request),
            "cache": "miss",
        },
    }
    return cache_set(request.app.state, cache_key, payload, settings.CACHE_TTL_SECONDS)
