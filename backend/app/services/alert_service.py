def get_sorted_alerts(alerts):
    return sorted(alerts, key=lambda x: x.get("kenaikan_pct", 0), reverse=True)
