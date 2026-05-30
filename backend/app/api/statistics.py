from fastapi import APIRouter, Request

from app.core.config import settings
from app.services.catboost_prediction_service import get_national_statistics_from_catboost
from app.services.statistics_service import get_national_statistics

router = APIRouter()


@router.get("/statistik-nasional")
def get_statistik_nasional(request: Request):
    engine = getattr(request.app.state, "prediction_engine", settings.PREDICTION_ENGINE)
    if engine == "catboost":
        if hasattr(request.app.state, "cached_statistik_nasional") and request.app.state.cached_statistik_nasional:
            return request.app.state.cached_statistik_nasional
            
        return get_national_statistics_from_catboost(
            request.app.state.df_semua,
            request.app.state,
        )

    return get_national_statistics(request.app.state.df_semua, request.app.state.df_hasil)
