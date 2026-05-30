from pathlib import Path

import pandas as pd

from app.utils.converters import format_date, safe_float, to_slug


def load_dataset(dataset_path: str):
    try:
        path = Path(dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Dataset file tidak ditemukan: {path}")

        if path.suffix.lower() == ".parquet":
            df = pd.read_parquet(path)
        else:
            df = pd.read_csv(path)
        if "tanggal" in df.columns:
            df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

        required_columns = {"tanggal", "provinsi", "komoditas", "harga"}
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"Dataset tidak memiliki kolom wajib: {missing}")

        min_tanggal = df["tanggal"].min() if "tanggal" in df.columns else None
        max_tanggal = df["tanggal"].max() if "tanggal" in df.columns else None

        print(f"Dataset rows: {len(df)}")
        print(f"Dataset columns: {len(df.columns)}")
        print(f"Dataset min tanggal: {min_tanggal}")
        print(f"Dataset max tanggal: {max_tanggal}")
        return df
    except Exception as exc:
        raise RuntimeError("Failed to load dataset") from exc


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


def normalize_lookup_key(value: str) -> str:
    if value is None:
        return ""
    return " ".join(str(value).strip().lower().split())


def build_historical_index(df_semua):
    if df_semua is None or df_semua.empty:
        return {}
    has_harga_nasional_col = "harga_nasional" in df_semua.columns
    index = {}
    for (provinsi, komoditas), subset in df_semua.groupby(["provinsi", "komoditas"]):
        sorted_subset = subset.sort_values("tanggal")
        nasional_map = (
            df_semua[df_semua["komoditas"] == komoditas]
            .groupby("tanggal", as_index=True)["harga"]
            .mean()
            .to_dict()
        )
        rows = []
        for _, row in sorted_subset.iterrows():
            harga_nasional_val = row.get("harga_nasional") if has_harga_nasional_col else None
            harga_nasional = safe_float(harga_nasional_val)
            if harga_nasional is None:
                harga_nasional = safe_float(nasional_map.get(row["tanggal"]))
            rows.append(
                {
                    "tanggal": format_date(row["tanggal"]),
                    "harga": safe_float(row["harga"]),
                    "harga_nasional": harga_nasional,
                    "status_pasokan": row.get("status_pasokan", "NORMAL"),
                }
            )
        index[(normalize_lookup_key(provinsi), normalize_lookup_key(komoditas))] = rows
    return index


def get_harga_historis_indexed(app_state, komoditas: str, provinsi: str):
    key = (normalize_lookup_key(provinsi), normalize_lookup_key(komoditas))
    historical_index = getattr(app_state, "historical_by_key", None)
    if historical_index and key in historical_index:
        return historical_index[key]
    return get_harga_historis(app_state.df_semua, komoditas, provinsi)


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
