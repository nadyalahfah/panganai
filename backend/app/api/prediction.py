from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Request

from app.core.config import settings
from app.services.dataset_service import resolve_komoditas_value, resolve_provinsi_value
from app.services.catboost_prediction_service import (
    get_all_province_predictions_legacy_contract,
    predict_single,
)
from app.services.live_prediction_service import predict_h7, predict_recursive_30
from app.services.runtime_cache_service import cache_get, cache_set
from app.services.prediction_csv_service import (
    get_all_province_predictions,
    get_daily_forecast,
    get_prediction_summary,
)

router = APIRouter()


def _engine(request: Request) -> str:
    return getattr(request.app.state, "prediction_engine", settings.PREDICTION_ENGINE)


@router.get("/prediksi")
def get_prediksi(komoditas: str, provinsi: str, request: Request):
    source_df = request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    provinsi_resolved = resolve_provinsi_value(source_df, provinsi)
    if not komoditas_resolved or not provinsi_resolved:
        raise HTTPException(
            status_code=404, detail="Slug komoditas/provinsi tidak ditemukan"
        )

    if _engine(request) == "catboost":
        source_df_predict = (
            request.app.state.latest_feature_df
            if hasattr(request.app.state, "latest_feature_df")
            and request.app.state.latest_feature_df is not None
            else request.app.state.feature_df
        )
        result = predict_single(
            df=source_df_predict,
            model=request.app.state.model,
            feature_columns=request.app.state.feature_columns,
            provinsi=provinsi_resolved,
            komoditas=komoditas_resolved,
            jenis_harga="pasar_tradisional",
            horizon=30,
        )
        return {
            "ringkasan": {
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
                "engine": "catboost",
                "prototype_recursive_forecast": True,
            },
            "harian": result["harian"],
            "prediksi_model": {
                "ringkasan": {
                    "harga_sekarang": result["harga_sekarang"],
                    "prediksi_7h": result["prediksi_7h"],
                    "prediksi_30h": result["prediksi_30h"],
                    "tren_7h": result["tren_7h"],
                    "tren_30h": result["tren_30h"],
                },
                "harian": result["harian"],
                "source": "catboost_h01_h30_full_factor",
            },
        }

    ringkasan = get_prediction_summary(
        request.app.state.df_hasil, komoditas_resolved, provinsi_resolved
    )
    harian = get_daily_forecast(
        request.app.state.df_harian, komoditas_resolved, provinsi_resolved
    )
    return {
        "ringkasan": ringkasan,
        "harian": harian,
        "prediksi_model": {
            "ringkasan": ringkasan,
            "harian": harian,
            "source": "csv_fallback",
        },
    }


@router.get("/prediksi-semua")
def get_prediksi_semua(komoditas: str, request: Request):
    source_df = request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    if not komoditas_resolved:
        raise HTTPException(status_code=404, detail="Slug komoditas tidak ditemukan")

    if _engine(request) == "catboost":
        cache_key = f"prediksi_semua::{komoditas_resolved}"
        cached = cache_get(request.app.state, cache_key)
        if cached is not None:
            return cached

        if (
            hasattr(request.app.state, "cached_prediksi_all")
            and request.app.state.cached_prediksi_all
        ):
            if komoditas_resolved in request.app.state.cached_prediksi_all:
                return cache_set(
                    request.app.state,
                    cache_key,
                    request.app.state.cached_prediksi_all[komoditas_resolved],
                    settings.CACHE_TTL_SECONDS,
                )

        rows = get_all_province_predictions_legacy_contract(
            request.app.state, komoditas_resolved
        )
        payload = [{**row, "engine": "catboost"} for row in rows]
        return cache_set(request.app.state, cache_key, payload, settings.CACHE_TTL_SECONDS)

    return get_all_province_predictions(request.app.state.df_hasil, komoditas_resolved)


@router.get("/prediksi-live")
def get_prediksi_live(
    provinsi: str,
    komoditas: str,
    request: Request,
    horizon: int = 7,
    jenis_harga: Optional[str] = None,
    level_harga: Optional[str] = None,
):
    source_df = request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    provinsi_resolved = resolve_provinsi_value(source_df, provinsi)
    if not komoditas_resolved or not provinsi_resolved:
        raise HTTPException(
            status_code=404, detail="Slug komoditas/provinsi tidak ditemukan"
        )

    if horizon > 30:
        raise HTTPException(
            status_code=400, detail="Maksimum horizon live inference adalah 30 hari."
        )

    if horizon <= 7:
        result = predict_h7(
            app_state=request.app.state,
            provinsi=provinsi_resolved,
            komoditas=komoditas_resolved,
            jenis_harga=jenis_harga,
            level_harga=level_harga,
        )
        return {"mode": "live_catboost", **result}

    result = predict_recursive_30(
        app_state=request.app.state,
        provinsi=provinsi_resolved,
        komoditas=komoditas_resolved,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    )
    predictions = [
        {
            "tanggal": row["target_date"],
            "horizon": row["horizon"],
            "prediksi_harga": row["prediksi_harga"],
        }
        for row in result["predictions"]
    ]

    return {
        "mode": "live_catboost",
        "prototype_recursive_forecast": True,
        "provinsi": result["provinsi"],
        "komoditas": result["komoditas"],
        "last_data_date": result["last_data_date"],
        "predictions": predictions,
        "prediksi_harian": result.get("prediksi_harian", []),
    }


@router.post("/prediksi-batch")
def get_prediksi_batch(
    request: Request,
    pairs: List[dict] = Body(..., example=[{"komoditas": "beras-medium-i", "provinsi": "aceh"}]),
):
    source_df = request.app.state.df_semua
    result = []

    for pair in pairs:
        komoditas_input = pair.get("komoditas")
        provinsi_input = pair.get("provinsi")
        komoditas_resolved = resolve_komoditas_value(source_df, komoditas_input)
        provinsi_resolved = resolve_provinsi_value(source_df, provinsi_input)

        if not komoditas_resolved or not provinsi_resolved:
            result.append(
                {
                    "komoditas": komoditas_input,
                    "provinsi": provinsi_input,
                    "found": False,
                    "detail": "Slug komoditas/provinsi tidak ditemukan",
                }
            )
            continue

        if _engine(request) == "catboost":
            source_df_predict = (
                request.app.state.latest_feature_df
                if hasattr(request.app.state, "latest_feature_df")
                and request.app.state.latest_feature_df is not None
                else request.app.state.feature_df
            )
            pred = predict_single(
                df=source_df_predict,
                model=request.app.state.model,
                feature_columns=request.app.state.feature_columns,
                provinsi=provinsi_resolved,
                komoditas=komoditas_resolved,
                jenis_harga="pasar_tradisional",
                horizon=30,
            )
            payload = {
                "ringkasan": {
                    "harga_sekarang": pred["harga_sekarang"],
                    "prediksi_7h": pred["prediksi_7h"],
                    "prediksi_30h": pred["prediksi_30h"],
                    "tren_7h": pred["tren_7h"],
                    "tren_30h": pred["tren_30h"],
                    "mape_pct": pred["mape_pct"],
                    "bawah_7h": pred["bawah_7h"],
                    "atas_7h": pred["atas_7h"],
                    "bawah_30h": pred["bawah_30h"],
                    "atas_30h": pred["atas_30h"],
                    "mae": pred["mae"],
                    "engine": "catboost",
                    "prototype_recursive_forecast": True,
                },
                "harian": pred["harian"],
            }
        else:
            payload = {
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

        result.append(
            {
                "komoditas": komoditas_input,
                "provinsi": provinsi_input,
                "found": True,
                "data": payload,
            }
        )

    return {"items": result}
