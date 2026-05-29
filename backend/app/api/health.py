from fastapi import APIRouter, Request

from app.utils.converters import format_date

router = APIRouter()


@router.get("/")
async def root():
    return {
        "status": "success",
        "message": "API Pangan AI siap melayani permintaan data harga pangan Indonesia.",
    }


@router.get("/api/health")
def health(request: Request):
    data_loaded = all(
        hasattr(request.app.state, attr)
        for attr in ("df_hasil", "df_harian", "df_semua", "alerts")
    )
    model_loaded = getattr(request.app.state, "model", None) is not None and len(
        getattr(request.app.state, "feature_columns", [])
    ) > 0

    return {
        "status": "ok",
        "data_loaded": data_loaded,
        "model_loaded": model_loaded,
        "data_source": "csv_snapshot",
    }


@router.get("/api/model-info")
def model_info(request: Request):
    model_loaded = getattr(request.app.state, "model", None) is not None
    prediction_engine = getattr(request.app.state, "prediction_engine", "unknown")
    feature_columns = getattr(request.app.state, "feature_columns", [])
    feature_df = getattr(request.app.state, "feature_df", None)

    if feature_df is None or feature_df.empty:
        return {
            "model_loaded": model_loaded,
            "feature_count": len(feature_columns),
            "prediction_engine": prediction_engine,
            "dataset_rows": 0,
            "min_date": None,
            "max_date": None,
            "available_provinsi_count": 0,
            "available_komoditas_count": 0,
        }

    tanggal_series = feature_df["tanggal"] if "tanggal" in feature_df.columns else None
    min_date = format_date(tanggal_series.min()) if tanggal_series is not None else None
    max_date = format_date(tanggal_series.max()) if tanggal_series is not None else None

    return {
        "model_loaded": model_loaded,
        "feature_count": len(feature_columns),
        "prediction_engine": prediction_engine,
        "dataset_rows": int(len(feature_df)),
        "min_date": min_date,
        "max_date": max_date,
        "available_provinsi_count": int(feature_df["provinsi"].nunique())
        if "provinsi" in feature_df.columns
        else 0,
        "available_komoditas_count": int(feature_df["komoditas"].nunique())
        if "komoditas" in feature_df.columns
        else 0,
    }
