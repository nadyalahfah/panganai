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
    DATASET_FEATURE_ENGINEERED_PATH = DATA_DIR / "final_training_dataset_feature_engineered.csv"
    DATASET_SEMUA_PATH = DATA_DIR / "semua_komoditas.csv"
    MODEL_DIR = ROOT_DIR / "models"

    USE_AZURE_BLOB = os.getenv("USE_AZURE_BLOB", "true").lower() == "true"
    AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING", "")
    AZURE_BLOB_CONTAINER = os.getenv("AZURE_BLOB_CONTAINER", "")

    # New artifact configuration
    AZURE_MODEL_BLOB = os.getenv("AZURE_MODEL_BLOB", "models/catboost_h01_h30_full_factor.cbm")
    AZURE_INFERENCE_INPUT_BLOB = os.getenv(
        "AZURE_INFERENCE_INPUT_BLOB", "datasets/model_input_2026-05-20_h01_h30.parquet"
    )
    AZURE_HISTORICAL_PRICE_PARQUET_BLOB = os.getenv(
        "AZURE_HISTORICAL_PRICE_PARQUET_BLOB", "datasets/harga_historis_2026-01-01_2026-05-20.parquet"
    )

    LOCAL_MODEL_PATH = os.getenv("LOCAL_MODEL_PATH", ".cache/catboost_h01_h30_full_factor.cbm")
    LOCAL_INFERENCE_INPUT_PATH = os.getenv(
        "LOCAL_INFERENCE_INPUT_PATH", ".cache/model_input_2026-05-20_h01_h30.parquet"
    )
    LOCAL_HISTORICAL_PRICE_PARQUET_PATH = os.getenv(
        "LOCAL_HISTORICAL_PRICE_PARQUET_PATH", ".cache/harga_historis_2026-01-01_2026-05-20.parquet"
    )

    # Optional files
    MODEL_MANIFEST_PATH = os.getenv(
        "MODEL_MANIFEST_PATH", str(ROOT_DIR / "reports" / "modeling" / "model_manifest_full_factor.json")
    )
    LOCAL_HISTORICAL_CSV_FALLBACK_PATH = os.getenv(
        "LOCAL_HISTORICAL_CSV_FALLBACK_PATH", str(DATA_DIR / "harga_historis_2026-01-01_2026-05-20.csv")
    )
    LOCAL_HISTORICAL_SUMMARY_PARQUET_PATH = os.getenv(
        "LOCAL_HISTORICAL_SUMMARY_PARQUET_PATH", str(DATA_DIR / "harga_historis_summary_2026-01-01_2026-05-20.parquet")
    )

    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "300"))
    PREDICTION_ENGINE = "catboost"

    # Backward-compatible aliases
    CATBOOST_MODEL_PATH = Path(LOCAL_MODEL_PATH)
    FEATURE_COLUMNS_PATH = Path(".cache/feature_columns.pkl")

    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "https://panganai-xaii.services.ai.azure.com/openai/v1")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
    AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-4.1-mini")

    AI_INSIGHT_ENABLE_CACHE = os.getenv("AI_INSIGHT_ENABLE_CACHE", "true").lower() == "true"
    AI_INSIGHT_CACHE_TTL_SECONDS = int(os.getenv("AI_INSIGHT_CACHE_TTL_SECONDS", "21600"))
    AI_INSIGHT_FALLBACK_TTL_SECONDS = int(os.getenv("AI_INSIGHT_FALLBACK_TTL_SECONDS", "300"))
    AI_INSIGHT_RATE_GUARD_SECONDS = int(os.getenv("AI_INSIGHT_RATE_GUARD_SECONDS", "30"))
    ALERT_MIN_CHANGE_PCT = float(os.getenv("ALERT_MIN_CHANGE_PCT", "5"))

    CORS_ALLOWED_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000,https://panganai.vercel.app",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()
