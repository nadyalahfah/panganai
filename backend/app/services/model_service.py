from __future__ import annotations

import pickle
from pathlib import Path

import pandas as pd
from catboost import CatBoostRegressor


class ModelService:
    @staticmethod
    def load_model(model_path) -> CatBoostRegressor:
        path = Path(model_path)
        if not path.exists():
            raise FileNotFoundError(f"CatBoost model file tidak ditemukan: {path}")
        model = CatBoostRegressor()
        model.load_model(str(path))
        return model

    @staticmethod
    def load_feature_columns(feature_columns_path) -> list[str]:
        path = Path(feature_columns_path)
        if not path.exists():
            raise FileNotFoundError(f"Feature columns file tidak ditemukan: {path}")
        with open(path, "rb") as f:
            return pickle.load(f)

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
