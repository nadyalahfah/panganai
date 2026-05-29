from app.services.feature_service import get_latest_feature_row
from app.services.live_prediction_service import build_live_prediction_response
from app.utils.converters import safe_float


def build_csv_prediction_response(df_hasil, df_harian, komoditas: str, provinsi: str):
    mask_r = (df_hasil["komoditas"] == komoditas) & (df_hasil["provinsi"] == provinsi)
    row_r = df_hasil[mask_r]

    ringkasan = {}
    if not row_r.empty:
        r = row_r.iloc[0]
        ringkasan = {
            "harga_sekarang": safe_float(r["harga_sekarang"]),
            "prediksi_7h": safe_float(r["prediksi_7h"]),
            "prediksi_30h": safe_float(r["prediksi_30h"]),
            "tren_7h": r["tren_7h"],
            "tren_30h": r["tren_30h"],
            "mape_pct": safe_float(r["mape_pct"]),
            "bawah_7h": safe_float(r["bawah_7h"]),
            "atas_7h": safe_float(r["atas_7h"]),
            "bawah_30h": safe_float(r["bawah_30h"]),
            "atas_30h": safe_float(r["atas_30h"]),
            "mae": safe_float(r["mae"]),
        }

    mask_h = (df_harian["komoditas"] == komoditas) & (df_harian["provinsi"] == provinsi)
    subset_h = df_harian[mask_h].sort_values("tanggal")

    harian = []
    for _, row in subset_h.iterrows():
        harian.append(
            {
                "tanggal": row["tanggal"].strftime("%Y-%m-%d"),
                "prediksi": safe_float(row["prediksi"]),
                "batas_bawah": safe_float(row["batas_bawah"]),
                "batas_atas": safe_float(row["batas_atas"]),
            }
        )

    return {"ringkasan": ringkasan, "harian": harian}


def build_live_prediction(feature_df, model, feature_columns, komoditas: str, provinsi: str):
    row = get_latest_feature_row(feature_df, komoditas, provinsi)
    return build_live_prediction_response(model, row, feature_columns)
