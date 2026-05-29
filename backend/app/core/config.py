from pathlib import Path

class Settings:
    ROOT_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = ROOT_DIR / "data"
    PREDICTIONS_CSV_DIR = DATA_DIR / "predictions" / "csv"
    PREDICTIONS_JSON_DIR = DATA_DIR / "predictions" / "json"
    DATASET_DIR = DATA_DIR / "dataset" / "clean_dataset"
    DATASET_LATEST_PATH = DATA_DIR / "dataset" / "latest_dataset.csv"
    DATASET_FEATURE_ENGINEERED_PATH = DATA_DIR / "dataset" / "final_training_dataset_feature_engineered.csv"
    DATASET_SEMUA_PATH = DATASET_DIR / "semua_komoditas.csv"
    MODEL_DIR = ROOT_DIR / "models"
    CATBOOST_MODEL_PATH = MODEL_DIR / "trained_catboost_model.cbm"
    FEATURE_COLUMNS_PATH = MODEL_DIR / "feature_columns.pkl"
    PREDICTION_ENGINE = "catboost"
    ENABLE_CSV_FALLBACK = True


settings = Settings()
