from django.shortcuts import render
from collections import defaultdict

from apps.knowledge.models import QuestionHistory
from .weather_alerts import get_agricultural_alerts
from .weather_services import get_current_weather 


def home_view(request):
    # 📚 Historique des questions par catégorie (5 dernières)
    historique = defaultdict(list)

    for q in QuestionHistory.objects.all().order_by("-created_at")[:5]:
        historique[q.theme].append(q.question)

    # 🌤️ Météo actuelle (auto IP, mondial)
    meteo = get_current_weather(request)

    # 🚜 Alertes agricoles météo
    alertes_agricoles = get_agricultural_alerts(request)

    return render(request, "home.html", {
        "historique_questions": historique.items(),
        "meteo": meteo,
        "alertes_agricoles": alertes_agricoles,
    })
