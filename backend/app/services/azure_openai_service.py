import hashlib
import json
import logging
import threading
import time
from datetime import datetime, timezone

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

FALLBACK_JSON = {
    "summary": "Forecast generated successfully.",
    "risk": "No AI analysis available.",
    "recommendation": "Use forecast values as reference.",
}

_CACHE_LOCK = threading.Lock()
_INSIGHT_CACHE: dict[str, dict] = {}
_INFLIGHT_EVENTS: dict[str, threading.Event] = {}
_LAST_MISS_TS: dict[str, float] = {}


def _now() -> float:
    return time.time()


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_payload(
    commodity_name: str,
    current_price: float,
    predicted_price: float,
    change_percent: float,
    recommendation_data: str,
) -> dict:
    return {
        "commodity": str(commodity_name or "").strip().lower(),
        "current_price": round(float(current_price), 2),
        "predicted_price": round(float(predicted_price), 2),
        "change_percent": round(float(change_percent), 2),
        "recommendation_data": str(recommendation_data or "").strip(),
    }


def _cache_key_from_payload(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def _get_cached(key: str):
    if not settings.AI_INSIGHT_ENABLE_CACHE:
        return None
    ts = _now()
    with _CACHE_LOCK:
        row = _INSIGHT_CACHE.get(key)
        if not row:
            return None
        if row["expires_at"] < ts:
            _INSIGHT_CACHE.pop(key, None)
            return None
        return row


def _set_cached(key: str, payload: dict, ttl_seconds: int):
    if not settings.AI_INSIGHT_ENABLE_CACHE:
        return
    with _CACHE_LOCK:
        _INSIGHT_CACHE[key] = {
            "value": payload,
            "expires_at": _now() + max(1, ttl_seconds),
        }


def _can_miss_now(key: str) -> bool:
    with _CACHE_LOCK:
        last = _LAST_MISS_TS.get(key, 0.0)
        if (_now() - last) < settings.AI_INSIGHT_RATE_GUARD_SECONDS:
            return False
        _LAST_MISS_TS[key] = _now()
        return True


def _acquire_or_wait(key: str):
    with _CACHE_LOCK:
        evt = _INFLIGHT_EVENTS.get(key)
        if evt is None:
            evt = threading.Event()
            _INFLIGHT_EVENTS[key] = evt
            return evt, True
    logger.info("insight.dedup_wait key=%s", key)
    evt.wait(timeout=10)
    return evt, False


def _release_inflight(key: str):
    with _CACHE_LOCK:
        evt = _INFLIGHT_EVENTS.pop(key, None)
        if evt:
            evt.set()


def get_client():
    if not settings.AZURE_OPENAI_API_KEY:
        return None
    return OpenAI(
        api_key=settings.AZURE_OPENAI_API_KEY,
        base_url=settings.AZURE_OPENAI_ENDPOINT,
        timeout=5.0,
    )


def _call_azure(payload: dict) -> dict:
    client = get_client()
    if not client:
        logger.warning("Fallback activated: Azure OpenAI client not initialized (missing API key).")
        return dict(FALLBACK_JSON)

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
        f"Commodity: {payload['commodity']}\n"
        f"Current Price: {payload['current_price']}\n"
        f"Predicted Price: {payload['predicted_price']}\n"
        f"Change Percent: {payload['change_percent']}%\n"
        f"Recommendation Data: {payload['recommendation_data']}"
    )

    logger.info("insight.azure_call key_payload_commodity=%s", payload["commodity"])
    response = client.chat.completions.create(
        model=settings.AZURE_OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = response.choices[0].message.content
    parsed_json = json.loads(content)
    for key in ["summary", "risk", "recommendation"]:
        if key not in parsed_json:
            parsed_json[key] = ""
    return parsed_json


def generate_market_insight(
    commodity_name: str,
    current_price: float,
    predicted_price: float,
    change_percent: float,
    recommendation_data: str = "",
) -> dict:
    payload = _normalize_payload(
        commodity_name=commodity_name,
        current_price=current_price,
        predicted_price=predicted_price,
        change_percent=change_percent,
        recommendation_data=recommendation_data,
    )
    key = _cache_key_from_payload(payload)

    cached = _get_cached(key)
    if cached is not None:
        logger.info("insight.cache_hit key=%s", key)
        val = dict(cached["value"])
        val.update({"cache_hit": True, "cache_key": key})
        return val

    evt, is_leader = _acquire_or_wait(key)
    if not is_leader:
        cached_after_wait = _get_cached(key)
        if cached_after_wait is not None:
            logger.info("insight.cache_hit key=%s", key)
            val = dict(cached_after_wait["value"])
            val.update({"cache_hit": True, "cache_key": key})
            return val

    try:
        if not _can_miss_now(key):
            cached_guard = _get_cached(key)
            if cached_guard is not None:
                val = dict(cached_guard["value"])
                val.update({"cache_hit": True, "cache_key": key})
                return val
            # Return short fallback to stop retry storms.
            logger.info("insight.fallback_returned reason=rate_guard key=%s", key)
            fallback_val = {
                **FALLBACK_JSON,
                "generated_at": _iso_now(),
                "cache_hit": False,
                "cache_key": key,
            }
            _set_cached(key, fallback_val, settings.AI_INSIGHT_FALLBACK_TTL_SECONDS)
            return fallback_val

        try:
            insight = _call_azure(payload)
            result = {
                **insight,
                "generated_at": _iso_now(),
                "cache_hit": False,
                "cache_key": key,
            }
            _set_cached(key, result, settings.AI_INSIGHT_CACHE_TTL_SECONDS)
            return result
        except Exception as exc:
            logger.error("Response failure: Exception occurred during AI generation: %s", exc)
            logger.info("insight.fallback_returned reason=azure_error key=%s", key)
            fallback_val = {
                **FALLBACK_JSON,
                "generated_at": _iso_now(),
                "cache_hit": False,
                "cache_key": key,
            }
            _set_cached(key, fallback_val, settings.AI_INSIGHT_FALLBACK_TTL_SECONDS)
            return fallback_val
    finally:
        _release_inflight(key)
