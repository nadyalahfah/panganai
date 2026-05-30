from __future__ import annotations

import argparse
import math
from pathlib import Path
import pickle
import sys

import pandas as pd


def _format_bytes(num_bytes: int) -> str:
    if num_bytes <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    idx = min(int(math.log(num_bytes, 1024)), len(units) - 1)
    val = num_bytes / (1024**idx)
    return f"{val:.2f} {units[idx]}"


def _load_feature_columns(path: Path) -> list[str]:
    with path.open("rb") as f:
        cols = pickle.load(f)
    if not isinstance(cols, (list, tuple)):
        raise ValueError("feature_columns.pkl harus berisi list/tuple nama kolom.")
    return [str(c) for c in cols]


def _ensure_columns(df: pd.DataFrame, required: list[str], label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{label}: kolom wajib tidak ditemukan: {missing}")


def generate(
    input_csv: Path,
    feature_columns_path: Path,
    output_dir: Path,
    history_days: int = 90,
) -> None:
    try:
        import pyarrow  # noqa: F401
    except Exception as exc:
        raise RuntimeError(
            "Parquet engine belum terpasang. Install dulu: "
            "`pip install pyarrow` atau `pip install -r backend/requirements.txt`."
        ) from exc

    if not input_csv.exists():
        raise FileNotFoundError(f"CSV input tidak ditemukan: {input_csv}")
    if not feature_columns_path.exists():
        raise FileNotFoundError(f"feature_columns.pkl tidak ditemukan: {feature_columns_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_out = output_dir / "latest_inference_snapshot.parquet"
    historical_out = output_dir / "historical_chart_sample.parquet"

    feature_columns = _load_feature_columns(feature_columns_path)

    df = pd.read_csv(input_csv, low_memory=False)
    _ensure_columns(
        df,
        ["tanggal", "provinsi", "komoditas", "jenis_harga", "level_harga", "harga"],
        "Dataset input",
    )

    df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
    df = df.dropna(subset=["tanggal"]).copy()
    df = df.sort_values("tanggal", ascending=True)

    meta_cols = ["tanggal", "provinsi", "komoditas", "jenis_harga", "level_harga", "harga"]
    keep_for_snapshot = list(dict.fromkeys(meta_cols + feature_columns))
    existing_keep_for_snapshot = [c for c in keep_for_snapshot if c in df.columns]

    snapshot_df = (
        df.groupby(["provinsi", "komoditas", "jenis_harga", "level_harga"], dropna=False, as_index=False)
        .tail(1)
        .copy()
    )
    snapshot_df = snapshot_df[existing_keep_for_snapshot]

    drop_targets = [c for c in snapshot_df.columns if c.lower().startswith("harga_target_") or c.lower().startswith("target")]
    if drop_targets:
        snapshot_df = snapshot_df.drop(columns=drop_targets, errors="ignore")

    chart_cols = ["tanggal", "provinsi", "komoditas", "jenis_harga", "level_harga", "harga"]
    chart_cols = [c for c in chart_cols if c in df.columns]
    max_date = df["tanggal"].max()
    min_date = df["tanggal"].min()
    min_history_date = max_date - pd.Timedelta(days=history_days)
    historical_df = df[df["tanggal"] >= min_history_date][chart_cols].copy()

    snapshot_df.to_parquet(snapshot_out, index=False, compression="snappy")
    historical_df.to_parquet(historical_out, index=False, compression="snappy")

    original_size = input_csv.stat().st_size
    snapshot_size = snapshot_out.stat().st_size
    historical_size = historical_out.stat().st_size

    print("Original Dataset:")
    print(f"Rows: {len(df):,}")
    print(f"Size: {_format_bytes(original_size)}")
    print()
    print("Inference Snapshot:")
    print(f"Rows: {len(snapshot_df):,}")
    print(f"Size: {_format_bytes(snapshot_size)}")
    print()
    print("Historical Sample:")
    print(f"Rows: {len(historical_df):,}")
    print(f"Size: {_format_bytes(historical_size)}")
    print()
    print("Date Range:")
    print(f"{min_date.strftime('%Y-%m-%d')} -> {max_date.strftime('%Y-%m-%d')}")
    print()
    print("Output Files:")
    print(snapshot_out)
    print(historical_out)


def main() -> None:
    backend_dir = Path(__file__).resolve().parent
    default_csv = backend_dir / "data" / "dataset" / "final_training_dataset_feature_engineered.csv"
    default_feature_cols = backend_dir / "models" / "feature_columns.pkl"
    default_output = backend_dir / "output"

    parser = argparse.ArgumentParser(description="Generate lightweight inference/chart snapshots from training CSV.")
    parser.add_argument("--input-csv", type=Path, default=default_csv)
    parser.add_argument("--feature-columns", type=Path, default=default_feature_cols)
    parser.add_argument("--output-dir", type=Path, default=default_output)
    parser.add_argument("--history-days", type=int, default=90)
    args = parser.parse_args()

    generate(
        input_csv=args.input_csv,
        feature_columns_path=args.feature_columns,
        output_dir=args.output_dir,
        history_days=args.history_days,
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)
