from fastapi import APIRouter, Request, Response

from app.core.config import settings
from app.services.catboost_prediction_service import get_alerts_from_catboost
from app.services.alert_service import get_sorted_alerts

router = APIRouter()


@router.get("/alert")
def get_alert(request: Request, response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    engine = getattr(request.app.state, "prediction_engine", settings.PREDICTION_ENGINE)
    if engine == "catboost":
        if hasattr(request.app.state, "cached_alerts") and request.app.state.cached_alerts is not None:
            return request.app.state.cached_alerts
        return get_alerts_from_catboost(request.app.state)

    return get_sorted_alerts(request.app.state.alerts)
