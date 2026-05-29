import pandas as pd
import re


def safe_float(val):
    try:
        if pd.isna(val):
            return None
        return round(float(val), 2)
    except Exception:
        return None


def safe_int(val):
    try:
        if pd.isna(val):
            return None
        return int(val)
    except Exception:
        return None


def format_date(date):
    try:
        if pd.isna(date):
            return None
        return pd.to_datetime(date).strftime("%Y-%m-%d")
    except Exception:
        return None


def to_slug(value: str):
    if value is None:
        return None
    text = str(value).strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")
