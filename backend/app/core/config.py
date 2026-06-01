import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Settings:
    ROOT_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = ROOT_DIR / "data"
    PREDICTIONS_CSV_DIR = DATA_DIR / "predictions" / "csv"
    PREDICTIONS_JSON_DIR = DATA_DIR / "predictions" / "json"
    DATASET_DIR = DATA_DIR
    DATASET_LATEST_PATH = DATA_DIR / "latest_dataset.csv"
    DATASET_FEATURE_ENGINEERED_PATH = (
        DATA_DIR / "final_training_dataset_feature_engineered.csv"
    )
    DATASET_SEMUA_PATH = DATA_DIR / "semua_komoditas.csv"
    MODEL_DIR = ROOT_DIR / "models"

    USE_AZURE_BLOB = os.getenv("USE_AZURE_BLOB", "true").lower() == "true"
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "")
    DATASET_BLOB_PATH = os.getenv(
        "DATASET_BLOB_PATH", "datasets/latest_inference_snapshot.parquet"
    )
    HISTORICAL_BLOB_PATH = os.getenv(
        "HISTORICAL_BLOB_PATH", "datasets/historical_chart_sample.parquet"
    )
    MODEL_BLOB_PATH = os.getenv("MODEL_BLOB_PATH", "models/trained_catboost_model.cbm")
    FEATURE_COLUMNS_BLOB_PATH = os.getenv(
        "FEATURE_COLUMNS_BLOB_PATH", "models/feature_columns.pkl"
    )

    LOCAL_DATASET_PATH = os.getenv(
        "LOCAL_DATASET_PATH", ".cache/latest_inference_snapshot.parquet"
    )
    LOCAL_HISTORICAL_PATH = os.getenv(
        "LOCAL_HISTORICAL_PATH", ".cache/historical_chart_sample.parquet"
    )
    LOCAL_MODEL_PATH = os.getenv(
        "LOCAL_MODEL_PATH", ".cache/trained_catboost_model.cbm"
    )
    LOCAL_FEATURE_COLUMNS_PATH = os.getenv(
        "LOCAL_FEATURE_COLUMNS_PATH", ".cache/feature_columns.pkl"
    )
    LATEST_INFERENCE_SNAPSHOT_PATH = os.getenv(
        "LATEST_INFERENCE_SNAPSHOT_PATH",
        str(DATA_DIR / "latest_inference_snapshot.parquet"),
    )
    HISTORICAL_CHART_SAMPLE_PATH = os.getenv(
        "HISTORICAL_CHART_SAMPLE_PATH",
        str(DATA_DIR / "historical_chart_sample.parquet"),
    )
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))

    # Backward-compatible aliases used by legacy modules.
    CATBOOST_MODEL_PATH = Path(LOCAL_MODEL_PATH)
    FEATURE_COLUMNS_PATH = Path(LOCAL_FEATURE_COLUMNS_PATH)
    PREDICTION_ENGINE = "catboost"

    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://panganai-xaii.services.ai.azure.com/openai/v1")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini")


settings = Settings()
