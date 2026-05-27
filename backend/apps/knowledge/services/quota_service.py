# apps/knowledge/services/quota_service.py

from datetime import date
from threading import Lock

# ==========================================================
# 🌱 Quotas par plan
# ==========================================================
FREE_DAILY_LIMIT = 20
PRO_DAILY_LIMIT = 300

# Lock thread-safe pour mise à jour user.daily_requests
_lock = Lock()


# ==========================================================
# 🔹 Vérifie et met à jour le quota utilisateur
# ==========================================================
def check_user_quota(user) -> bool:
    """
    Vérifie si l'utilisateur peut encore faire une requête aujourd'hui.
    Incrémente daily_requests si autorisé.
    
    Args:
        user: instance du modèle User (doit avoir `plan`, `daily_requests`, `last_request_date`)
    
    Returns:
        bool: True si la requête est autorisée, False si quota dépassé
    """

    today = date.today()

    with _lock:
        # 🔹 Reset du compteur si nouveau jour
        if user.last_request_date != today:
            user.daily_requests = 0
            user.last_request_date = today
            user.save()

        # 🔹 Sélection limite selon plan
        limit = PRO_DAILY_LIMIT if getattr(user, "plan", "free") == "pro" else FREE_DAILY_LIMIT

        if getattr(user, "daily_requests", 0) >= limit:
            return False

        # 🔹 Incrémentation safe
        user.daily_requests = getattr(user, "daily_requests", 0) + 1
        user.save()

        return True