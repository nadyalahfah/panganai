from fastapi import HTTPException
from types import SimpleNamespace
from datetime import timedelta
import pandas as pd

from app.services.feature_service import get_latest_row
from app.services.live_prediction_service import predict_h7, predict_recursive_30
from app.utils.converters import format_date, safe_float


def _trend_label(pred, current):
    if pred > current:
        return "NAIK"
    if pred < current:
        return "TURUN"
    return "STABIL"


def _build_legacy_summary(h7_result, h30_result, rolling_std_7=None):
    harga_sekarang = safe_float(h7_result.get("harga_sekarang"))
    pred7 = safe_float(h7_result.get("prediksi_harga"))

    weekly_preds = h30_result.get("predictions", [])
    pred30_raw = weekly_preds[-1]["prediksi_harga"] if weekly_preds else pred7
    pred30 = safe_float(pred30_raw)

    tren_7h = _trend_label(pred7 or 0, harga_sekarang or 0)
    tren_30h = _trend_label(pred30 or 0, harga_sekarang or 0)

    # Prototype uncertainty metrics (non-null for frontend compatibility)
    if rolling_std_7 is None or rolling_std_7 <= 0:
        mae_7 = abs((pred7 or 0) * 0.03)
    else:
        mae_7 = abs(float(rolling_std_7))
    mae_30 = mae_7 * 2.0

    bawah_7h = (pred7 - mae_7) if pred7 is not None else None
    atas_7h = (pred7 + mae_7) if pred7 is not None else None
    bawah_30h = (pred30 - mae_30) if pred30 is not None else None
    atas_30h = (pred30 + mae_30) if pred30 is not None else None

    mae = mae_7
    mape_pct = ((mae / abs(harga_sekarang)) * 100) if harga_sekarang else 0

    return {
        "harga_sekarang": harga_sekarang,
        "prediksi_7h": pred7,
        "prediksi_30h": pred30,
        "tren_7h": tren_7h,
        "tren_30h": tren_30h,
        "mape_pct": safe_float(mape_pct),
        "bawah_7h": safe_float(bawah_7h),
        "atas_7h": safe_float(atas_7h),
        "bawah_30h": safe_float(bawah_30h),
        "atas_30h": safe_float(atas_30h),
        "mae": safe_float(mae),
    }


def _segment_values(start_val: float, end_val: float, days: int):
    vals = []
    for i in range(1, days + 1):
        ratio = i / days
        vals.append(start_val + ((end_val - start_val) * ratio))
    return vals


def _build_legacy_daily(h7_result, h30_result, rolling_std_7=None):
    last_data_date = pd.to_datetime(h7_result["last_data_date"])
    harga_sekarang = float(h7_result["harga_sekarang"])

    pred_map = {row["horizon"]: float(row["prediksi_harga"]) for row in h30_result.get("predictions", [])}
    pred_7 = pred_map.get(7, float(h7_result["prediksi_harga"]))
    pred_14 = pred_map.get(14, pred_7)
    pred_21 = pred_map.get(21, pred_14)
    pred_28 = pred_map.get(28, pred_21)

    values = []
    values.extend(_segment_values(harga_sekarang, pred_7, 7))     # day 1-7
    values.extend(_segment_values(pred_7, pred_14, 7))            # day 8-14
    values.extend(_segment_values(pred_14, pred_21, 7))           # day 15-21
    values.extend(_segment_values(pred_21, pred_28, 7))           # day 22-28

    slope_last = (pred_28 - pred_21) / 7
    values.append(pred_28 + slope_last)       # day 29
    values.append(pred_28 + (2 * slope_last)) # day 30

    daily = []
    for idx, pred in enumerate(values, start=1):
        tanggal = format_date(last_data_date + timedelta(days=idx))
        if rolling_std_7 is not None and rolling_std_7 > 0:
            batas_bawah = pred - rolling_std_7
            batas_atas = pred + rolling_std_7
        else:
            margin = pred * 0.03
            batas_bawah = pred - margin
            batas_atas = pred + margin

        daily.append(
            {
                "tanggal": tanggal,
                "prediksi": safe_float(pred),
                "batas_bawah": safe_float(batas_bawah),
                "batas_atas": safe_float(batas_atas),
            }
        )
    return daily


def predict_single(
    df,
    model,
    feature_columns,
    provinsi,
    komoditas,
    jenis_harga=None,
    level_harga=None,
    horizon=30,
):
    latest_row = get_latest_row(
        df=df,
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    )
    app_state = SimpleNamespace(
        feature_df=df,
        model=model,
        feature_columns=feature_columns,
    )

    h7_result = predict_h7(
        app_state,
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    )
    h30_result = predict_recursive_30(
        app_state,
        provinsi=provinsi,
        komoditas=komoditas,
        jenis_harga=jenis_harga,
        level_harga=level_harga,
    )

    rolling_std_7 = latest_row.get("rolling_std_7", None)
    try:
        rolling_std_7 = float(rolling_std_7) if rolling_std_7 == rolling_std_7 else None
    except Exception:
        rolling_std_7 = None
    summary = _build_legacy_summary(h7_result, h30_result, rolling_std_7=rolling_std_7)

    harian = _build_legacy_daily(h7_result, h30_result, rolling_std_7=rolling_std_7)
    if horizon <= 7:
        harian = harian[:7]

    return {
        "provinsi": provinsi,
        "komoditas": komoditas,
        "harga_sekarang": summary["harga_sekarang"],
        "last_data_date": h7_result.get("last_data_date"),
        "target_date_7h": h7_result.get("target_date"),
        "prediksi_7h": summary["prediksi_7h"],
        "prediksi_30h": summary["prediksi_30h"],
        "tren_7h": summary["tren_7h"],
        "tren_30h": summary["tren_30h"],
        "prototype_recursive_forecast": True,
        "forecast_30h_source": "recursive_h7_to_h28",
        "note": "Prototype recursive forecast berbasis model H+7, bukan model native H+30.",
        "bawah_7h": summary["bawah_7h"],
        "atas_7h": summary["atas_7h"],
        "bawah_30h": summary["bawah_30h"],
        "atas_30h": summary["atas_30h"],
        "mape_pct": summary["mape_pct"],
        "mae": summary["mae"],
        "harian": harian,
    }


def predict_all_provinces(
    df,
    model,
    feature_columns,
    komoditas,
):
    provinces = sorted(df["provinsi"].dropna().unique().tolist())
    result = []

    for provinsi in provinces:
        try:
            row = predict_single(
                df=df,
                model=model,
                feature_columns=feature_columns,
                provinsi=provinsi,
                komoditas=komoditas,
                horizon=30,
            )
        except HTTPException as exc:
            if exc.status_code == 404:
                continue
            raise

        harga = row["harga_sekarang"]
        pred7 = row["prediksi_7h"]
        pred30 = row["prediksi_30h"]

        ubah_7_pct = round((pred7 - harga) / harga * 100, 1) if harga and pred7 else 0
        ubah_30_pct = round((pred30 - harga) / harga * 100, 1) if harga and pred30 else 0

        result.append(
            {
                "provinsi": provinsi,
                "harga_sekarang": harga,
                "prediksi_7h": pred7,
                "prediksi_30h": pred30,
                "tren_7h": row["tren_7h"],
                "tren_30h": row["tren_30h"],
                "ubah_7_pct": ubah_7_pct,
                "ubah_30_pct": ubah_30_pct,
            }
        )

    return result


def get_prediction_legacy_contract(app_state, komoditas, provinsi):
    source_df = app_state.latest_feature_df if hasattr(app_state, "latest_feature_df") and app_state.latest_feature_df is not None else app_state.feature_df
    full = predict_single(
        df=source_df,
        model=app_state.model,
        feature_columns=app_state.feature_columns,
        provinsi=provinsi,
        komoditas=komoditas,
        horizon=30,
    )

    return {
        "ringkasan": {
            "harga_sekarang": full["harga_sekarang"],
            "prediksi_7h": full["prediksi_7h"],
            "prediksi_30h": full["prediksi_30h"],
            "tren_7h": full["tren_7h"],
            "tren_30h": full["tren_30h"],
            "mape_pct": full["mape_pct"],
            "bawah_7h": full["bawah_7h"],
            "atas_7h": full["atas_7h"],
            "bawah_30h": full["bawah_30h"],
            "atas_30h": full["atas_30h"],
            "mae": full["mae"],
        },
        "harian": full["harian"],
    }


def get_all_province_predictions_legacy_contract(app_state, komoditas):
    source_df = app_state.latest_feature_df if hasattr(app_state, "latest_feature_df") and app_state.latest_feature_df is not None else app_state.feature_df
    return predict_all_provinces(
        df=source_df,
        model=app_state.model,
        feature_columns=app_state.feature_columns,
        komoditas=komoditas,
    )


def get_alerts_from_catboost(app_state, kenaikan_min_pct=5.0):
    alerts = []
    if hasattr(app_state, "latest_feature_df") and app_state.latest_feature_df is not None:
        latest_rows = app_state.latest_feature_df.copy()
    else:
        latest_rows = (
            app_state.feature_df.sort_values("tanggal")
            .groupby(["provinsi", "komoditas"], as_index=False)
            .tail(1)
            .copy()
        )

    pangan_score_threshold = None
    if "pangan_risk_score" in latest_rows.columns and not latest_rows["pangan_risk_score"].dropna().empty:
        pangan_score_threshold = float(latest_rows["pangan_risk_score"].quantile(0.75))

    for _, latest in latest_rows.iterrows():
        provinsi = latest["provinsi"]
        komoditas = latest["komoditas"]
        jenis_harga = latest.get("jenis_harga")
        level_harga = latest.get("level_harga")

        try:
            pred_h7 = predict_h7(
                app_state,
                provinsi=provinsi,
                komoditas=komoditas,
                jenis_harga=jenis_harga if jenis_harga == jenis_harga else None,
                level_harga=level_harga if level_harga == level_harga else None,
            )
        except HTTPException as exc:
            if exc.status_code == 404:
                continue
            raise

        harga_sekarang = pred_h7["harga_sekarang"]
        prediksi_7h = pred_h7["prediksi_harga"]
        tren_7h = _trend_label(prediksi_7h or 0, harga_sekarang or 0)
        kenaikan_pct = (
            round((prediksi_7h - harga_sekarang) / harga_sekarang * 100, 1)
            if harga_sekarang and prediksi_7h
            else 0
        )

        risk_level = str(latest.get("risk_level", "UNKNOWN"))
        ai_reasoning = str(latest.get("ai_reasoning", ""))
        pangan_risk_score = latest.get("pangan_risk_score")
        try:
            pangan_risk_score = float(pangan_risk_score)
        except Exception:
            pangan_risk_score = None

        high_risk_score = (
            pangan_risk_score is not None
            and pangan_score_threshold is not None
            and pangan_risk_score >= pangan_score_threshold
        )

        should_alert = (
            kenaikan_pct >= kenaikan_min_pct
            or tren_7h == "NAIK"
            or risk_level.upper() == "HIGH"
            or high_risk_score
        )
        if not should_alert:
            continue

        alerts.append(
            {
                "provinsi": provinsi,
                "komoditas": komoditas,
                "harga_sekarang": harga_sekarang,
                "prediksi_7h": prediksi_7h,
                "kenaikan_pct": kenaikan_pct,
                "risk_level": risk_level,
                "ai_reasoning": ai_reasoning,
                "engine": "catboost",
            }
        )

    return sorted(alerts, key=lambda x: x.get("kenaikan_pct", 0), reverse=True)


def get_national_statistics_from_catboost(df_semua, app_state):
    latest_date = df_semua["tanggal"].max()
    today_data = df_semua[df_semua["tanggal"] == latest_date]

    result = []
    for komoditas in sorted(today_data["komoditas"].unique().tolist()):
        kom_data = today_data[today_data["komoditas"] == komoditas]
        harga_avg = safe_float(kom_data["harga"].mean())

        pred_all = get_all_province_predictions_legacy_contract(app_state, komoditas)
        if pred_all:
            tren_counts = {}
            for row in pred_all:
                tren = row.get("tren_30h", "STABIL")
                tren_counts[tren] = tren_counts.get(tren, 0) + 1
            tren_mayoritas = max(tren_counts, key=tren_counts.get)
        else:
            tren_mayoritas = "STABIL"

        result.append(
            {
                "komoditas": komoditas,
                "harga_rata_nasional": harga_avg,
                "tren_30h_mayoritas": tren_mayoritas,
                "engine": "catboost",
            }
        )

    return result
