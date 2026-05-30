from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.repositories.alert_repository import load_alerts
from app.repositories.dataset_repository import load_main_dataset, resolve_main_dataset_path
from app.repositories.prediction_repository import load_daily_prediction, load_prediction_summary
from app.services.feature_service import _resolve_feature_dataset_path, load_feature_dataset
from app.services.model_service import ModelService

from app.services.catboost_prediction_service import (
    get_alerts_from_catboost,
    get_all_province_predictions_legacy_contract,
    get_national_statistics_from_catboost,
)
from app.services.dataset_service import get_komoditas_objects, get_provinsi_objects

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
    logger.info("Loading main dataset...")
    app.state.df_semua = load_main_dataset()
    if app.state.df_semua is not None:
        mem_usage = app.state.df_semua.memory_usage(deep=True).sum() / (1024**2)
        logger.info(f"df_semua loaded: {len(app.state.df_semua):,} rows | {len(app.state.df_semua.columns)} cols | Memory: {mem_usage:.2f} MB")
    try:
        app.state.alerts = load_alerts()
    except FileNotFoundError:
        app.state.alerts = []
    app.state.prediction_engine = settings.PREDICTION_ENGINE
    app.state.model = None
    app.state.feature_columns = []
    app.state.feature_df = None
    app.state.latest_feature_df = None

    if settings.PREDICTION_ENGINE == "catboost":
        try:
            app.state.model = ModelService.load_model(settings.CATBOOST_MODEL_PATH)
            app.state.feature_columns = ModelService.load_feature_columns(settings.FEATURE_COLUMNS_PATH)
            logger.info("Loading feature dataset...")
            app.state.feature_df = load_feature_dataset(app.state.feature_columns)
            if app.state.feature_df is not None:
                mem_usage = app.state.feature_df.memory_usage(deep=True).sum() / (1024**2)
                logger.info(f"Feature dataset loaded: {app.state.feature_df.shape} | Memory: {mem_usage:.2f} MB")
            
            # Pre-compute latest rows for O(1) filtering during inference
            if not app.state.feature_df.empty:
                group_cols = ["provinsi", "komoditas"]
                if "jenis_harga" in app.state.feature_df.columns:
                    group_cols.append("jenis_harga")
                if "level_harga" in app.state.feature_df.columns:
                    group_cols.append("level_harga")
                idx = app.state.feature_df.groupby(group_cols, dropna=False)["tanggal"].idxmax()
                app.state.latest_feature_df = app.state.feature_df.loc[idx].copy()
                mem_usage = app.state.latest_feature_df.memory_usage(deep=True).sum() / (1024**2)
                logger.info(f"latest_feature_df loaded: {app.state.latest_feature_df.shape} | Memory: {mem_usage:.2f} MB")
            else:
                app.state.latest_feature_df = None
                
            app.state.prediction_engine = "catboost"

            # Phase 2 Precomputations
            df_feature_source = app.state.latest_feature_df if app.state.latest_feature_df is not None else app.state.feature_df
            
            logger.info("Building cached komoditas...")
            app.state.cached_komoditas = get_komoditas_objects(df_feature_source)
            logger.info(f"cached_komoditas: {len(app.state.cached_komoditas)} records")

            logger.info("Building cached provinsi...")
            app.state.cached_provinsi = get_provinsi_objects(df_feature_source)
            logger.info(f"cached_provinsi: {len(app.state.cached_provinsi)} records")

            logger.info("Building cached statistics...")
            app.state.cached_statistik_nasional = get_national_statistics_from_catboost(app.state.df_semua, app.state)
            logger.info(f"cached_statistik_nasional: {len(app.state.cached_statistik_nasional)} records")

            logger.info("Building cached alerts...")
            app.state.cached_alerts = get_alerts_from_catboost(app.state)
            logger.info(f"cached_alerts: {len(app.state.cached_alerts)} records")

            logger.info("Building cached predictions...")
            cached_prediksi_all = {}
            for k_obj in app.state.cached_komoditas:
                kom_name = k_obj["nama"]
                preds = get_all_province_predictions_legacy_contract(app.state, kom_name)
                cached_prediksi_all[kom_name] = [{**row, "engine": "catboost"} for row in preds]
            app.state.cached_prediksi_all = cached_prediksi_all
            logger.info(f"cached_prediksi_all: {sum(len(v) for v in app.state.cached_prediksi_all.values())} records")
            logger.info("Cache ready.")
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
