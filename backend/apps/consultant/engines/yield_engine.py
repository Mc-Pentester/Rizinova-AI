class YieldEngine:

    def simulate(self, surface, current_yield, improvement_percent=15):
        new_yield = current_yield * (1 + improvement_percent / 100)
        total_production = new_yield * surface

        return {
            "surface_ha": surface,
            "current_yield": current_yield,
            "new_yield_per_ha": round(new_yield, 2),
            "total_production": round(total_production, 2),
        }