from app.utils.converters import safe_float


def get_national_statistics(df_semua, df_hasil):
    latest_date = df_semua["tanggal"].max()
    today_data = df_semua[df_semua["tanggal"] == latest_date]

    result = []
    for komoditas in today_data["komoditas"].unique():
        kom_data = today_data[today_data["komoditas"] == komoditas]
        harga_avg = safe_float(kom_data["harga"].mean())

        pred_kom = df_hasil[df_hasil["komoditas"] == komoditas]
        if not pred_kom.empty:
            tren_counts = pred_kom["tren_30h"].value_counts()
            tren_mayoritas = tren_counts.index[0] if len(tren_counts) > 0 else "STABIL"
        else:
            tren_mayoritas = "STABIL"

        result.append(
            {
                "komoditas": komoditas,
                "harga_rata_nasional": harga_avg,
                "tren_30h_mayoritas": tren_mayoritas,
            }
        )
    return result
