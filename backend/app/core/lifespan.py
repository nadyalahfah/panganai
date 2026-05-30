from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.repositories.alert_repository import load_alerts
from app.repositories.dataset_repository import load_main_dataset, resolve_main_dataset_path
from app.repositories.prediction_repository import load_daily_prediction, load_prediction_summary
from app.services.feature_service import _resolve_feature_dataset_path, load_feature_dataset
from app.services.feature_service import build_latest_features_index
from app.services.model_service import ModelService
from app.services.catboost_prediction_service import (
    get_alerts_from_catboost,
    get_all_province_predictions_legacy_contract,
    get_national_statistics_from_catboost,
)
from app.services.dataset_service import get_komoditas_objects, get_provinsi_objects
from app.services.dataset_service import build_historical_index
from app.services.blob_storage_service import BlobStorageService
from app.services.dataset_service import load_dataset
from app.services.model_service import load_catboost_model, load_feature_columns
import pandas as pd
from pathlib import Path

logger = logging.getLogger("panganai")


def _validate_startup_files() -> None:
    dataset_main_path = resolve_main_dataset_path()
    required_files = [dataset_main_path]
    if settings.PREDICTION_ENGINE == "catboost":
        required_files.extend([settings.CATBOOST_MODEL_PATH, settings.FEATURE_COLUMNS_PATH])
    if settings.PREDICTION_ENGINE == "csv":
        required_files.extend([
            settings.PREDICTIONS_CSV_DIR / "hasil_prediksi.csv",
            settings.PREDICTIONS_CSV_DIR / "prediksi_harian.csv",
            settings.PREDICTIONS_JSON_DIR / "alert_prediksi.json",
        ])
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"File startup wajib tidak ditemukan: {missing}")


@asynccontextmanager
async def lifespan(app):
    try:
        app.state.runtime_cache = {}
        app.state.dashboard_initial_cache = None
        app.state.prediction_all_cache = {}
        app.state.statistics_cache = None
        app.state.alert_cache = None
        app.state.latest_inference_snapshot = None
        app.state.historical_chart_sample = None

        if not settings.USE_AZURE_BLOB:
            _validate_startup_files()
        # Download from Azure Blob if enabled, else use local
        current_settings = settings
        if current_settings.USE_AZURE_BLOB:
            blob_storage = BlobStorageService(current_settings)
            latest_inference_path = blob_storage.download_if_missing(
                current_settings.DATASET_BLOB_PATH,
                current_settings.LOCAL_DATASET_PATH,
            )
            historical_chart_path = blob_storage.download_if_missing(
                current_settings.HISTORICAL_BLOB_PATH,
                current_settings.LOCAL_HISTORICAL_PATH,
            )
            model_path = blob_storage.download_if_missing(
                current_settings.MODEL_BLOB_PATH,
                current_settings.LOCAL_MODEL_PATH,
            )
            feature_columns_path = blob_storage.download_if_missing(
                current_settings.FEATURE_COLUMNS_BLOB_PATH,
                current_settings.LOCAL_FEATURE_COLUMNS_PATH,
            )
        else:
            logger.info("USE_AZURE_BLOB=false, using local artifact paths.")
            latest_inference_path = current_settings.LOCAL_DATASET_PATH
            historical_chart_path = current_settings.LOCAL_HISTORICAL_PATH
            model_path = current_settings.LOCAL_MODEL_PATH
            feature_columns_path = current_settings.LOCAL_FEATURE_COLUMNS_PATH

        # Load prediction summary and daily prediction (CSV fallback)
        try:
            app.state.df_hasil = load_prediction_summary()
            app.state.df_harian = load_daily_prediction()
        except FileNotFoundError:
            app.state.df_hasil = None
            app.state.df_harian = None

        # Load main dataset
        logger.info("Loading main dataset...")
        app.state.df_semua = (
            load_main_dataset()
            if not current_settings.USE_AZURE_BLOB
            else load_dataset(historical_chart_path)
        )
        if app.state.df_semua is not None:
            mem_usage = app.state.df_semua.memory_usage(deep=True).sum() / (1024**2)
            logger.info(f"df_semua loaded: {len(app.state.df_semua):,} rows | {len(app.state.df_semua.columns)} cols | Memory: {mem_usage:.2f} MB")
            app.state.historical_by_key = build_historical_index(app.state.df_semua)
            logger.info(f"historical_by_key built: {len(app.state.historical_by_key):,} keys")

        # Load alerts
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
                # Load model and feature columns
                if current_settings.USE_AZURE_BLOB:
                    app.state.model = load_catboost_model(model_path)
                    app.state.feature_columns = load_feature_columns(feature_columns_path)
                else:
                    app.state.model = ModelService.load_model(settings.CATBOOST_MODEL_PATH)
                    app.state.feature_columns = ModelService.load_feature_columns(settings.FEATURE_COLUMNS_PATH)

                logger.info("Loading feature dataset...")
                if current_settings.USE_AZURE_BLOB:
                    app.state.feature_df = load_dataset(latest_inference_path)
                else:
                    app.state.feature_df = load_feature_dataset(app.state.feature_columns)
                if app.state.feature_df is not None:
                    mem_usage = app.state.feature_df.memory_usage(deep=True).sum() / (1024**2)
                    logger.info(f"Feature dataset loaded: {app.state.feature_df.shape} | Memory: {mem_usage:.2f} MB")

                # Pre-compute latest rows for O(1) filtering during inference
                if app.state.feature_df is not None and not app.state.feature_df.empty:
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
                app.state.latest_features_by_key = build_latest_features_index(app.state.latest_feature_df)
                logger.info(f"latest_features_by_key built: {len(app.state.latest_features_by_key):,} keys")

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
                if hasattr(settings, "ENABLE_CSV_FALLBACK") and settings.ENABLE_CSV_FALLBACK:
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

        # Optional parquet snapshots for faster dashboards
        try:
            latest_snapshot_path = current_settings.LATEST_INFERENCE_SNAPSHOT_PATH
            if latest_snapshot_path and Path(latest_snapshot_path).exists():
                app.state.latest_inference_snapshot = pd.read_parquet(latest_snapshot_path)
                logger.info(
                    "latest_inference_snapshot loaded: %s rows",
                    len(app.state.latest_inference_snapshot),
                )
        except Exception as exc:
            logger.warning("Failed loading latest_inference_snapshot.parquet: %s", exc)
        try:
            chart_sample_path = current_settings.HISTORICAL_CHART_SAMPLE_PATH
            if chart_sample_path and Path(chart_sample_path).exists():
                app.state.historical_chart_sample = pd.read_parquet(chart_sample_path)
                logger.info(
                    "historical_chart_sample loaded: %s rows",
                    len(app.state.historical_chart_sample),
                )
        except Exception as exc:
            logger.warning("Failed loading historical_chart_sample.parquet: %s", exc)
    except Exception as exc:
        logger.error(f"Startup failed: {exc}")
        raise

    yield
