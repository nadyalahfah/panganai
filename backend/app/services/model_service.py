from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor


def load_catboost_model(model_path: str):
    try:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"CatBoost model file tidak ditemukan: {path}")

        model = CatBoostRegressor()
        model.load_model(str(path))
        return model
    except Exception as exc:
        raise RuntimeError("Failed to load CatBoost model") from exc


def load_feature_columns(feature_path: str):
    try:
        path = Path(feature_path)
        if not path.exists():
            raise FileNotFoundError(f"Feature columns file tidak ditemukan: {path}")

        with open(path, "rb") as file:
            feature_columns = pickle.load(file)

        if not isinstance(feature_columns, list):
            raise ValueError("feature_columns.pkl harus berisi list feature.")

        print(f"Loaded feature columns: {len(feature_columns)}")
        return feature_columns
    except Exception as exc:
        raise RuntimeError("Failed to load feature columns") from exc


class ModelService:
    @staticmethod
    def load_model(model_path) -> CatBoostRegressor:
        return load_catboost_model(model_path)

    @staticmethod
    def load_feature_columns(feature_columns_path) -> list[str]:
        return load_feature_columns(feature_columns_path)

    @staticmethod
    def predict(model, x: pd.DataFrame, numeric_fill_values: dict | None = None):
        x_pred = x.copy()
        cat_indices = set(model.get_cat_feature_indices())
        for idx, col in enumerate(x_pred.columns):
            if idx in cat_indices:
                x_pred[col] = x_pred[col].fillna("unknown").astype(str)
            else:
                fill_value = 0.0
                if numeric_fill_values and col in numeric_fill_values:
                    fill_value = numeric_fill_values[col]
                x_pred[col] = pd.to_numeric(x_pred[col], errors="coerce").fillna(fill_value)
        return model.predict(x_pred)
