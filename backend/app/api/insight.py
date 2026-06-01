from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.azure_openai_service import generate_market_insight

router = APIRouter()

class InsightRequest(BaseModel):
    commodity: str
    current_price: float
    forecast_price: float
    change_percent: float
    recommendation_data: Optional[str] = ""

class InsightResponse(BaseModel):
    summary: str
    risk: str
    recommendation: str

@router.post("/insight", response_model=InsightResponse)
def get_ai_insight(request: InsightRequest):
    result = generate_market_insight(
        commodity_name=request.commodity,
        current_price=request.current_price,
        predicted_price=request.forecast_price,
        change_percent=request.change_percent,
        recommendation_data=request.recommendation_data
    )
    return result
