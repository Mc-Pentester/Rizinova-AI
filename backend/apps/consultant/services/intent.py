def detect_intent(query: str) -> str:
    q = query.lower()

    if any(w in q for w in ["rendement", "hectare", "production"]):
        return "yield_simulation"

    if any(w in q for w in ["profit", "rentable", "cout", "revenu"]):
        return "economic_analysis"

    if any(w in q for w in ["maladie", "champignon", "traitement"]):
        return "disease"

    return "general"