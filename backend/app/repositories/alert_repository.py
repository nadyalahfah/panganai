import json

from app.core.config import settings


def load_alerts():
    with open(settings.PREDICTIONS_JSON_DIR / "alert_prediksi.json", "r", encoding="utf-8") as f:
        return json.load(f)
