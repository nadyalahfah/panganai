from app.utils.converters import format_date, safe_float, to_slug


def get_komoditas(df_semua):
    return sorted(df_semua["komoditas"].dropna().astype(str).unique().tolist())


def get_provinsi(df_semua):
    return sorted(df_semua["provinsi"].dropna().astype(str).unique().tolist())


def get_komoditas_slug(df_semua):
    return sorted({to_slug(v) for v in get_komoditas(df_semua) if to_slug(v)})


def get_komoditas_objects(df_semua):
    nama_list = get_komoditas(df_semua)
    return [
        {
            "id": idx + 1,
            "nama": nama,
            "slug": to_slug(nama),
        }
        for idx, nama in enumerate(nama_list)
    ]


def get_provinsi_slug(df_semua):
    return sorted({to_slug(v) for v in get_provinsi(df_semua) if to_slug(v)})


def get_provinsi_objects(df_semua):
    nama_list = get_provinsi(df_semua)
    return [
        {
            "id": idx + 1,
            "nama": nama,
            "slug": to_slug(nama),
        }
        for idx, nama in enumerate(nama_list)
    ]


def resolve_komoditas_value(df, komoditas_value: str):
    values = get_komoditas(df)
    if komoditas_value in values:
        return komoditas_value
    slug_map = {to_slug(v): v for v in values}
    return slug_map.get(to_slug(komoditas_value))


def resolve_provinsi_value(df, provinsi_value: str):
    values = get_provinsi(df)
    if provinsi_value in values:
        return provinsi_value
    slug_map = {to_slug(v): v for v in values}
    return slug_map.get(to_slug(provinsi_value))


def get_harga_historis(df_semua, komoditas, provinsi):
    mask = (df_semua["komoditas"] == komoditas) & (df_semua["provinsi"] == provinsi)
    subset = df_semua[mask].sort_values("tanggal")

    # Fallback national price: mean harga per tanggal+komoditas
    has_harga_nasional_col = "harga_nasional" in df_semua.columns
    nasional_map = (
        df_semua[df_semua["komoditas"] == komoditas]
        .groupby("tanggal", as_index=True)["harga"]
        .mean()
        .to_dict()
    )

    result = []
    for _, row in subset.iterrows():
        harga_nasional_val = row.get("harga_nasional") if has_harga_nasional_col else None
        harga_nasional = safe_float(harga_nasional_val)
        if harga_nasional is None:
            harga_nasional = safe_float(nasional_map.get(row["tanggal"]))

        result.append(
            {
                "tanggal": format_date(row["tanggal"]),
                "harga": safe_float(row["harga"]),
                "harga_nasional": harga_nasional,
                "status_pasokan": row.get("status_pasokan", "NORMAL"),
            }
        )
    return result
