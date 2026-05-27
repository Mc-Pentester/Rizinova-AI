import requests
import os

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_current_weather(request):
    ip = request.META.get("REMOTE_ADDR", "")

    # 🧪 Cas développement local
    if ip in ("127.0.0.1", "::1") or ip.startswith("192.168."):
        query = "auto:ip"
    else:
        query = ip

    url = "https://api.weatherapi.com/v1/current.json"
    params = {
        "key": WEATHER_API_KEY,
        "q": query,
        "lang": "fr"
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()

        if "current" not in data:
            return None

        return {
            "ville": data["location"]["name"],
            "pays": data["location"]["country"],
            "temp": data["current"]["temp_c"],
            "condition": data["current"]["condition"]["text"],
            "icone": data["current"]["condition"]["icon"],
            "humidite": data["current"]["humidity"],
            "vent": data["current"]["wind_kph"],
        }

    except Exception:
        return None
