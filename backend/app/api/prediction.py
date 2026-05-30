from typing import Optional

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.services.dataset_service import resolve_komoditas_value, resolve_provinsi_value
from app.services.catboost_prediction_service import (
    get_all_province_predictions_legacy_contract,
    predict_single,
)
from app.services.live_prediction_service import predict_h7, predict_recursive_30
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
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    provinsi_resolved = resolve_provinsi_value(source_df, provinsi)
    if not komoditas_resolved or not provinsi_resolved:
        raise HTTPException(status_code=404, detail="Slug komoditas/provinsi tidak ditemukan")

    if _engine(request) == "catboost":
        source_df_predict = request.app.state.latest_feature_df if hasattr(request.app.state, "latest_feature_df") and request.app.state.latest_feature_df is not None else request.app.state.feature_df
        result = predict_single(
            df=source_df_predict,
            model=request.app.state.model,
            feature_columns=request.app.state.feature_columns,
            provinsi=provinsi_resolved,
            komoditas=komoditas_resolved,
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
        }

    ringkasan = get_prediction_summary(request.app.state.df_hasil, komoditas_resolved, provinsi_resolved)
    harian = get_daily_forecast(request.app.state.df_harian, komoditas_resolved, provinsi_resolved)
    return {"ringkasan": ringkasan, "harian": harian}


@router.get("/prediksi-semua")
def get_prediksi_semua(komoditas: str, request: Request):
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    if not komoditas_resolved:
        raise HTTPException(status_code=404, detail="Slug komoditas tidak ditemukan")

    if _engine(request) == "catboost":
        if hasattr(request.app.state, "cached_prediksi_all") and request.app.state.cached_prediksi_all:
            if komoditas_resolved in request.app.state.cached_prediksi_all:
                return request.app.state.cached_prediksi_all[komoditas_resolved]
                
        rows = get_all_province_predictions_legacy_contract(request.app.state, komoditas_resolved)
        return [{**row, "engine": "catboost"} for row in rows]

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
    source_df = request.app.state.feature_df if request.app.state.feature_df is not None else request.app.state.df_semua
    komoditas_resolved = resolve_komoditas_value(source_df, komoditas)
    provinsi_resolved = resolve_provinsi_value(source_df, provinsi)
    if not komoditas_resolved or not provinsi_resolved:
        raise HTTPException(status_code=404, detail="Slug komoditas/provinsi tidak ditemukan")

    if _engine(request) != "catboost":
        raise HTTPException(status_code=400, detail="Endpoint /api/prediksi-live hanya tersedia saat engine catboost aktif.")

    if horizon > 30:
        raise HTTPException(status_code=400, detail="Maksimum horizon live inference adalah 30 hari.")

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
