from contextlib import asynccontextmanager
import logging
from pathlib import Path

import pandas as pd

from app.core.config import settings
from app.repositories.alert_repository import load_alerts
from app.repositories.prediction_repository import load_daily_prediction, load_prediction_summary
from app.services.blob_storage_service import BlobStorageService
from app.services.catboost_prediction_service import (
    CatBoostPredictionService,
    get_alerts_from_catboost,
    get_all_province_predictions_legacy_contract,
    get_national_statistics_from_catboost,
)
from app.services.dataset_service import build_historical_index, get_komoditas_objects, get_provinsi_objects
from app.services.price_datasets_service import PriceDatasetsService

logger = logging.getLogger("panganai")


@asynccontextmanager
async def lifespan(app):
    try:
        app.state.runtime_cache = {}
        app.state.dashboard_initial_cache = None
        app.state.prediction_all_cache = {}
        app.state.statistics_cache = None
        app.state.alert_cache = None

        app.state.df_hasil = None
        app.state.df_harian = None
        app.state.alerts = []

        # Optional CSV fallback data
        try:
            app.state.df_hasil = load_prediction_summary()
            app.state.df_harian = load_daily_prediction()
        except FileNotFoundError:
            pass
        try:
            app.state.alerts = load_alerts()
        except FileNotFoundError:
            pass

        current_settings = settings

        model_path = current_settings.LOCAL_MODEL_PATH
        inference_input_path = current_settings.LOCAL_INFERENCE_INPUT_PATH
        historical_parquet_path = current_settings.LOCAL_HISTORICAL_PRICE_PARQUET_PATH

        model_artifacts_ready = True

        storage_ready = False
        storage_error = None

        if current_settings.USE_AZURE_BLOB:
            try:
                blob_storage = BlobStorageService(current_settings)
                storage_ready = True
            except Exception as exc:
                blob_storage = None
                storage_error = str(exc)
                model_artifacts_ready = Path(model_path).exists() and Path(inference_input_path).exists()
                logger.error(
                    "Azure Blob Storage unavailable, continuing with local artifacts if present: %s",
                    exc,
                )

            if blob_storage is not None:
                try:
                    model_path = blob_storage.download_blob_if_needed(
                        current_settings.AZURE_MODEL_BLOB,
                        current_settings.LOCAL_MODEL_PATH,
                    )
                    inference_input_path = blob_storage.download_blob_if_needed(
                        current_settings.AZURE_INFERENCE_INPUT_BLOB,
                        current_settings.LOCAL_INFERENCE_INPUT_PATH,
                    )
                except Exception as exc:
                    model_artifacts_ready = Path(model_path).exists() and Path(inference_input_path).exists()
                    logger.error("Model artifacts unavailable from blob storage: %s", exc)

                try:
                    historical_parquet_path = blob_storage.download_blob_if_needed(
                        current_settings.AZURE_HISTORICAL_PRICE_PARQUET_BLOB,
                        current_settings.LOCAL_HISTORICAL_PRICE_PARQUET_PATH,
                    )
                except Exception as exc:
                    logger.error("Historical artifact download failed (will fallback to CSV if possible): %s", exc)
        else:
            logger.info("USE_AZURE_BLOB=false, using local artifacts directly.")
            model_artifacts_ready = Path(model_path).exists() and Path(inference_input_path).exists()

        logger.info(
            "Startup artifacts | model_blob=%s model_local=%s input_blob=%s history_blob=%s",
            current_settings.AZURE_MODEL_BLOB,
            model_path,
            current_settings.AZURE_INFERENCE_INPUT_BLOB,
            current_settings.AZURE_HISTORICAL_PRICE_PARQUET_BLOB,
        )

        # Load historical datasets service (non-fatal)
        app.state.price_datasets_service = PriceDatasetsService(
            historical_parquet_path=historical_parquet_path,
            historical_csv_fallback_path=current_settings.LOCAL_HISTORICAL_CSV_FALLBACK_PATH,
            summary_parquet_path=current_settings.LOCAL_HISTORICAL_SUMMARY_PARQUET_PATH,
        )
        app.state.price_datasets_service.load()
        price_status = app.state.price_datasets_service.get_status()
        logger.info(
            "Historical loaded | rows=%s date_range=%s..%s summary_rows=%s",
            price_status.get("history_rows"),
            price_status.get("history_date_min"),
            price_status.get("history_date_max"),
            price_status.get("summary_rows"),
        )

        history_df = app.state.price_datasets_service.history_df
        if history_df is not None and not history_df.empty:
            app.state.df_semua = history_df.copy()
            app.state.historical_by_key = build_historical_index(app.state.df_semua)
            logger.info("historical_by_key built: %s keys", len(app.state.historical_by_key))
        else:
            app.state.df_semua = pd.DataFrame()
            app.state.historical_by_key = {}

        # Load CatBoost prediction service (fatal for catboost engine availability)
        app.state.catboost_prediction_service = CatBoostPredictionService(
            model_path=model_path,
            input_parquet_path=inference_input_path,
            manifest_path=current_settings.MODEL_MANIFEST_PATH,
        )
        if model_artifacts_ready:
            app.state.catboost_prediction_service.load()
            app.state.catboost_prediction_service.predict_all()
        else:
            app.state.catboost_prediction_service.status.update(
                {
                    "available": False,
                    "loaded": False,
                    "predicted": False,
                    "error": "Model/input artifacts unavailable. Startup continues with CSV fallback.",
                }
            )
        pred_status = app.state.catboost_prediction_service.get_status()

        # Backward compatibility fields used by existing endpoints/services.
        app.state.model = app.state.catboost_prediction_service.model
        if app.state.model is not None:
            setattr(app.state.model, "_service_ref", app.state.catboost_prediction_service)
        app.state.feature_columns = app.state.catboost_prediction_service.feature_columns
        app.state.feature_df = app.state.catboost_prediction_service.input_df
        app.state.latest_feature_df = app.state.catboost_prediction_service.input_df

        logger.info(
            "CatBoost loaded | model_local=%s model_file_size=%s input_rows=%s input_cols=%s pred_rows=%s target_range=%s..%s",
            model_path,
            Path(model_path).stat().st_size if Path(model_path).exists() else None,
            pred_status.get("rows"),
            pred_status.get("columns"),
            pred_status.get("prediction_rows"),
            pred_status.get("target_date_min"),
            pred_status.get("target_date_max"),
        )

        if pred_status.get("available") and pred_status.get("predicted"):
            app.state.prediction_engine = "catboost"
        else:
            app.state.prediction_engine = "csv"
            logger.error("CatBoost unavailable, switching engine to csv: %s", pred_status.get("error"))

        # Build cached catalogs/statistics/alerts from loaded runtime sources.
        df_feature_source = app.state.feature_df if app.state.feature_df is not None else app.state.df_semua
        app.state.cached_komoditas = get_komoditas_objects(df_feature_source)
        app.state.cached_provinsi = get_provinsi_objects(df_feature_source)
        app.state.cached_statistik_nasional = get_national_statistics_from_catboost(app.state.df_semua, app.state)
        app.state.cached_alerts = get_alerts_from_catboost(app.state)

        cached_prediksi_all = {}
        for k_obj in app.state.cached_komoditas:
            kom_name = k_obj["nama"]
            preds = get_all_province_predictions_legacy_contract(app.state, kom_name)
            cached_prediksi_all[kom_name] = [{**row, "engine": "catboost"} for row in preds]
        app.state.cached_prediksi_all = cached_prediksi_all

        app.state.model_loaded = bool(pred_status.get("available") and pred_status.get("predicted"))
        app.state.dataset_loaded = bool(history_df is not None and not history_df.empty)
        app.state.storage_ready = storage_ready
        app.state.storage_error = storage_error

    except Exception as exc:
        logger.error("Startup failed: %s", exc)
        raise

    yield
