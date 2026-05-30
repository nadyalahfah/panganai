from datetime import timedelta

import pandas as pd

from app.services.feature_service import build_prediction_matrix, get_latest_row
from app.services.model_service import ModelService
from app.utils.converters import format_date, safe_float


def _interpolate_daily_predictions(start_date, start_price: float, end_price: float, days: int, horizon_offset: int = 0):
    daily = []
    for day in range(1, days + 1):
        ratio = day / days
        value = start_price + ((end_price - start_price) * ratio)
        daily.append(
            {
                "tanggal": format_date(start_date + timedelta(days=day)),
                "horizon": horizon_offset + day,
                "prediksi_harga": safe_float(value),
            }
        )
    return daily


def predict_h7(app_state, provinsi, komoditas, jenis_harga=None, level_harga=None):
    source_df = app_state.latest_feature_df if hasattr(app_state, "latest_feature_df") and app_state.latest_feature_df is not None else app_state.feature_df
    latest_row = get_latest_row(
        df=source_df,
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    )

    x = build_prediction_matrix(latest_row, app_state.feature_columns)
    pred = ModelService.predict(
        app_state.model,
        x,
        numeric_fill_values=getattr(app_state, "numeric_feature_medians", None),
    )[0]

    last_data_date = pd.to_datetime(latest_row["tanggal"])
    target_date = last_data_date + timedelta(days=7)
    harga_awal = float(latest_row.get("harga", pred))
    prediksi_harian = _interpolate_daily_predictions(
        start_date=last_data_date,
        start_price=harga_awal,
        end_price=float(pred),
        days=7,
        horizon_offset=0,
    )

    return {
        "provinsi": provinsi,
        "komoditas": komoditas,
        "harga_sekarang": safe_float(harga_awal),
        "last_data_date": format_date(last_data_date),
        "target_date": format_date(target_date),
        "horizon": 7,
        "prediksi_harga": safe_float(pred),
        "prediksi_harian": prediksi_harian,
    }


def _update_recursive_features(sim_row: pd.Series, predicted_price: float):
    prev_harga = float(sim_row.get("harga", predicted_price))

    sim_row["harga_lag_1"] = prev_harga
    sim_row["harga"] = predicted_price

    sim_row["rolling_mean_7"] = predicted_price
    sim_row["rolling_mean_14"] = predicted_price
    sim_row["rolling_mean_30"] = predicted_price

    if prev_harga != 0:
        sim_row["price_change_1"] = (predicted_price - prev_harga) / prev_harga
    else:
        sim_row["price_change_1"] = 0.0


def predict_recursive_30(app_state, provinsi, komoditas, jenis_harga=None, level_harga=None):
    source_df = app_state.latest_feature_df if hasattr(app_state, "latest_feature_df") and app_state.latest_feature_df is not None else app_state.feature_df
    latest_row = get_latest_row(
        df=source_df,
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    ).copy()

    current_date = pd.to_datetime(latest_row["tanggal"])
    current_price = float(latest_row.get("harga", 0.0))
    recursive_steps = []
    prediksi_harian = []

    for step in range(1, 5):
        x = build_prediction_matrix(latest_row, app_state.feature_columns)
        pred = float(
            ModelService.predict(
                app_state.model,
                x,
                numeric_fill_values=getattr(app_state, "numeric_feature_medians", None),
            )[0]
        )

        target_date = current_date + timedelta(days=7)
        recursive_steps.append(
            {
                "step": step,
                "horizon": step * 7,
                "target_date": format_date(target_date),
                "prediksi_harga": safe_float(pred),
            }
        )
        prediksi_harian.extend(
            _interpolate_daily_predictions(
                start_date=current_date,
                start_price=current_price,
                end_price=pred,
                days=7,
                horizon_offset=(step - 1) * 7,
            )
        )

        _update_recursive_features(latest_row, pred)
        current_price = pred
        latest_row["tanggal"] = target_date
        latest_row["bulan"] = target_date.month
        latest_row["tahun"] = target_date.year
        latest_row["hari_dalam_minggu"] = target_date.dayofweek
        latest_row["minggu_ke"] = int(target_date.isocalendar().week)
        current_date = target_date

    return {
        "provinsi": provinsi,
        "komoditas": komoditas,
        "last_data_date": format_date(pd.to_datetime(latest_row["tanggal"]) - timedelta(days=28)),
        "horizon": 30,
        "prototype_recursive_forecast": True,
        "note": "Prototype recursive forecast berbasis model H+7, bukan model native H+30.",
        "predictions": recursive_steps,
        "prediksi_harian": prediksi_harian,
    }
