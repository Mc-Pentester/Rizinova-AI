import os
import requests
from typing import List, Dict


WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_API_URL = "https://api.weatherapi.com/v1/forecast.json"


def get_client_ip(request):
    """
    Récupère l’IP réelle de l’utilisateur (compatible proxy / prod)
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR")


def get_agricultural_alerts(request) -> List[Dict[str, str]]:
    """
    Génère des alertes agricoles basées sur la météo locale (auto IP)
    """
    if not WEATHER_API_KEY:
        return []

    params = {
        "key": WEATHER_API_KEY,
        "q": "auto:ip",
        "days": 2,
        "alerts": "yes"
    }

    headers = {
        # permet à WeatherAPI de mieux détecter la localisation
        "X-Forwarded-For": get_client_ip(request)
    }

    try:
        response = requests.get(
            WEATHER_API_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
    except Exception:
        # En cas d’erreur réseau ou API → pas d’alerte
        return []

    alertes = []

    forecast_day = data.get("forecast", {}).get("forecastday", [])
    if not forecast_day:
        return []

    day = forecast_day[0]["day"]

    # 🌧️ Pluie excessive → risque inondation
    if day.get("totalprecip_mm", 0) >= 30:
        alertes.append({
            "message": "🌧️ Fortes pluies prévues : risque d’inondation des cultures"
        })

    # 🌡️ Chaleur excessive → stress hydrique
    if day.get("maxtemp_c", 0) >= 35:
        alertes.append({
            "message": "🌡️ Température très élevée : risque de stress hydrique"
        })

    # ☀️ Sécheresse → irrigation recommandée
    if day.get("totalprecip_mm", 0) < 2:
        alertes.append({
            "message": "☀️ Peu ou pas de pluie prévue : irrigation recommandée"
        })

    # 💨 Vent fort → dégâts possibles
    if day.get("maxwind_kph", 0) >= 40:
        alertes.append({
            "message": "💨 Vents forts attendus : risque de dégâts sur les cultures"
        })

    # 🚨 Alertes météo officielles
    for a in data.get("alerts", {}).get("alert", []):
        alertes.append({
            "message": f"🚨 Alerte météo officielle : {a.get('headline')}"
        })

    return alertes
