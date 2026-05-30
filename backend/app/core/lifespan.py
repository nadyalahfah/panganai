from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.repositories.alert_repository import load_alerts
from app.repositories.dataset_repository import load_main_dataset, resolve_main_dataset_path
from app.repositories.prediction_repository import load_daily_prediction, load_prediction_summary
from app.services.feature_service import _resolve_feature_dataset_path, load_feature_dataset
from app.services.model_service import ModelService

logger = logging.getLogger("panganai")


def _validate_startup_files():
    dataset_main_path = resolve_main_dataset_path()
    required_files = [dataset_main_path]
    if settings.PREDICTION_ENGINE == "catboost":
        required_files.extend([settings.CATBOOST_MODEL_PATH, settings.FEATURE_COLUMNS_PATH])
    if settings.PREDICTION_ENGINE == "csv":
        required_files.extend(
            [
                settings.PREDICTIONS_CSV_DIR / "hasil_prediksi.csv",
                settings.PREDICTIONS_CSV_DIR / "prediksi_harian.csv",
                settings.PREDICTIONS_JSON_DIR / "alert_prediksi.json",
            ]
        )
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"File startup wajib tidak ditemukan: {missing}")


@asynccontextmanager
async def lifespan(app):
    _validate_startup_files()
    dataset_main_path = resolve_main_dataset_path()
    feature_dataset_path = _resolve_feature_dataset_path()
    logger.info("Loading data files from CSV dir: %s", settings.PREDICTIONS_CSV_DIR)
    logger.info("Loading main dataset from: %s", dataset_main_path)
    logger.info("Loading feature dataset from: %s", feature_dataset_path)
    logger.info("Loading model file from: %s", settings.CATBOOST_MODEL_PATH)
    logger.info("Loading feature columns from: %s", settings.FEATURE_COLUMNS_PATH)

    try:
        app.state.df_hasil = load_prediction_summary()
        app.state.df_harian = load_daily_prediction()
    except FileNotFoundError:
        app.state.df_hasil = None
        app.state.df_harian = None
    app.state.df_semua = load_main_dataset()
    try:
        app.state.alerts = load_alerts()
    except FileNotFoundError:
        app.state.alerts = []
    app.state.prediction_engine = settings.PREDICTION_ENGINE
    app.state.model = None
    app.state.feature_columns = []
    app.state.feature_df = None

    if settings.PREDICTION_ENGINE == "catboost":
        try:
            app.state.model = ModelService.load_model(settings.CATBOOST_MODEL_PATH)
            app.state.feature_columns = ModelService.load_feature_columns(settings.FEATURE_COLUMNS_PATH)
            app.state.feature_df = load_feature_dataset()
            app.state.prediction_engine = "catboost"
        except Exception as exc:
            if settings.ENABLE_CSV_FALLBACK:
                fallback_files = [
                    settings.PREDICTIONS_CSV_DIR / "hasil_prediksi.csv",
                    settings.PREDICTIONS_CSV_DIR / "prediksi_harian.csv",
                    settings.PREDICTIONS_JSON_DIR / "alert_prediksi.json",
                ]
                missing_fallback = [str(path) for path in fallback_files if not path.exists()]
                if missing_fallback:
                    raise RuntimeError(
                        f"CatBoost gagal load dan file fallback CSV tidak lengkap: {missing_fallback}"
                    ) from exc
                logger.exception("CatBoost load gagal, fallback ke CSV diaktifkan: %s", exc)
                app.state.prediction_engine = "csv"
            else:
                raise RuntimeError(f"CatBoost gagal load dan fallback dimatikan: {exc}") from exc
    else:
        app.state.prediction_engine = "csv"

    df_feature = app.state.feature_df if app.state.feature_df is not None else app.state.df_semua
    if df_feature is not None and not df_feature.empty and "tanggal" in df_feature.columns:
        min_date = df_feature["tanggal"].min()
        max_date = df_feature["tanggal"].max()
    else:
        min_date = None
        max_date = None

    numeric_medians = {}
    if app.state.prediction_engine == "catboost" and df_feature is not None and not df_feature.empty:
        available_feature_cols = [c for c in app.state.feature_columns if c in df_feature.columns]
        numeric_part = df_feature[available_feature_cols].select_dtypes(include=["number"])
        numeric_medians = {
            col: float(val)
            for col, val in numeric_part.median(numeric_only=True).to_dict().items()
            if val == val
        }
    app.state.numeric_feature_medians = numeric_medians

    logger.info("Feature dataset rows: %s", len(df_feature))
    logger.info("Feature dataset min_date: %s", min_date)
    logger.info("Feature dataset max_date: %s", max_date)
    logger.info("Prediction engine active: %s", app.state.prediction_engine)
    logger.info("Model feature count: %s", len(app.state.feature_columns))
    logger.info("Model loaded: %s", app.state.model is not None)

    yield
