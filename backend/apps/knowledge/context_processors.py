from apps.knowledge.models import QuestionHistory


import random
from apps.knowledge.models import KnowledgeDocument

def quick_tips(request):
    """
    Fournit des conseils rapides aléatoires pour la sidebar
    """
    tips = (
        KnowledgeDocument.objects
        .only("title", "region")
    )

    tips_list = list(tips)

    # Sécurité si la base est vide
    if len(tips_list) < 3:
        selected = tips_list
    else:
        selected = random.sample(tips_list, 3)

    return {
        "quick_tips": selected
    }


def sidebar_history(request):
    data = {}

    qs = QuestionHistory.objects.order_by("-created_at")[:20]

    for q in qs:
        data.setdefault(q.theme, []).append(q.question)

    return {
        "historique_questions": data
    }
