REQUIRED_FIELDS = {
    "yield_simulation": ["surface_ha", "current_yield"],
    "economic_analysis": ["surface_ha", "yield_per_ha", "price_per_ton", "cost_per_ha"],
}

def check_missing_fields(intent: str, data: dict):
    required = REQUIRED_FIELDS.get(intent, [])
    missing = [field for field in required if field not in data]
    return missing