import json
import logging
from openai import OpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

FALLBACK_JSON = {
    "summary": "Forecast generated successfully.",
    "risk": "No AI analysis available.",
    "recommendation": "Use forecast values as reference."
}

def get_client():
    if not settings.AZURE_OPENAI_API_KEY:
        return None
    return OpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        base_url=settings.AZURE_OPENAI_ENDPOINT,
        timeout=5.0
    )

def generate_market_insight(
    commodity_name: str,
    current_price: float,
    predicted_price: float,
    change_percent: float,
    recommendation_data: str = ""
) -> dict:
    logger.info(f"Request start: Generating AI insight for {commodity_name}")
    client = get_client()
    
    if not client:
        logger.warning("Fallback activated: Azure OpenAI client not initialized (missing API key).")
        return FALLBACK_JSON
        
    system_prompt = (
        "You are an Indonesian food-price analyst.\n"
        "Your job is to explain forecast results in a concise, professional and actionable way.\n"
        "Return JSON only.\n"
        "Required schema:\n"
        "{\n"
        '  "summary": "...",\n'
        '  "risk": "...",\n'
        '  "recommendation": "..."\n'
        "}\n"
        "No markdown. No code block. No additional text."
    )
    
    user_context = (
        f"Commodity: {commodity_name}\n"
        f"Current Price: {current_price}\n"
        f"Predicted Price: {predicted_price}\n"
        f"Change Percent: {change_percent}%\n"
        f"Recommendation Data: {recommendation_data}"
    )

    try:
        response = client.chat.completions.create(
            model=settings.AZURE_OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_context}
            ],
            response_format={ "type": "json_object" },
            temperature=0.1
        )
        
        content = response.choices[0].message.content
        parsed_json = json.loads(content)
        
        # Enforce required keys
        for key in ["summary", "risk", "recommendation"]:
            if key not in parsed_json:
                parsed_json[key] = ""
                
        logger.info(f"Response success: AI insight generated for {commodity_name}")
        return parsed_json
        
    except Exception as e:
        logger.error(f"Response failure: Exception occurred during AI generation: {e}")
        logger.warning("Fallback activated: Returning deterministic fallback JSON.")
        return FALLBACK_JSON
