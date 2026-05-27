class EconomicEngine:

    def analyze(self, surface, yield_per_ha, price_per_ton, cost_per_ha):
        revenue = surface * yield_per_ha * price_per_ton
        total_cost = surface * cost_per_ha
        profit = revenue - total_cost

        return {
            "revenue": revenue,
            "total_cost": total_cost,
            "profit": profit
        }