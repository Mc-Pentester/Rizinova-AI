class RiskEngine:

    def evaluate(self, region=None, irrigation_type=None):
        risk_score = 0.2

        if irrigation_type == "pluvial":
            risk_score += 0.3

        return {
            "risk_score": risk_score,
            "risk_level": "High" if risk_score > 0.5 else "Moderate"
        }