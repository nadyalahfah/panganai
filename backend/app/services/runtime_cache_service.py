from datetime import datetime, timedelta


def cache_get(app_state, key: str):
    store = getattr(app_state, "runtime_cache", None)
    if not store:
        return None
    item = store.get(key)
    if not item:
        return None
    if item["expires_at"] <= datetime.utcnow():
        store.pop(key, None)
        return None
    return item["value"]


def cache_set(app_state, key: str, value, ttl_seconds: int):
    if not hasattr(app_state, "runtime_cache") or app_state.runtime_cache is None:
        app_state.runtime_cache = {}
    app_state.runtime_cache[key] = {
        "value": value,
        "expires_at": datetime.utcnow() + timedelta(seconds=ttl_seconds),
    }
    return value
