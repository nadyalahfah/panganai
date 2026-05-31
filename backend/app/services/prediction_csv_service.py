from app.utils.converters import format_date, safe_float


def get_prediction_summary(df_hasil, komoditas, provinsi):
    mask = (df_hasil["komoditas"] == komoditas) & (df_hasil["provinsi"] == provinsi)
    row = df_hasil[mask]

    if row.empty:
        return {}

    r = row.iloc[0]
    return {
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


def get_daily_forecast(df_harian, komoditas, provinsi):
    mask = (df_harian["komoditas"] == komoditas) & (df_harian["provinsi"] == provinsi)
    subset = df_harian[mask].sort_values("tanggal")

    result = []
    for _, row in subset.iterrows():
        result.append(
            {
                "tanggal": format_date(row["tanggal"]),
                "prediksi": safe_float(row["prediksi"]),
                "batas_bawah": safe_float(row["batas_bawah"]),
                "batas_atas": safe_float(row["batas_atas"]),
            }
        )
    return result


def get_all_province_predictions(df_hasil, komoditas):
    subset = df_hasil[df_hasil["komoditas"] == komoditas].copy()

    result = []
    for _, row in subset.iterrows():
        harga = safe_float(row["harga_sekarang"])
        pred7 = safe_float(row["prediksi_7h"])
        pred30 = safe_float(row["prediksi_30h"])

        # Create an interpolated 1 day prediction for CSV fallback
        pred1 = harga + ((pred7 - harga) * 1/7) if harga and pred7 else harga

        ubah_1_pct = round((pred1 - harga) / harga * 100, 1) if harga and pred1 else 0
        ubah_7_pct = round((pred7 - harga) / harga * 100, 1) if harga and pred7 else 0
        ubah_30_pct = round((pred30 - harga) / harga * 100, 1) if harga and pred30 else 0

        result.append(
            {
                "provinsi": row["provinsi"],
                "harga_sekarang": harga,
                "prediksi_1h": pred1,
                "prediksi_7h": pred7,
                "prediksi_30h": pred30,
                "tren_7h": row["tren_7h"],
                "tren_30h": row["tren_30h"],
                "ubah_1_pct": ubah_1_pct,
                "ubah_7_pct": ubah_7_pct,
                "ubah_30_pct": ubah_30_pct,
            }
        )
    return result
