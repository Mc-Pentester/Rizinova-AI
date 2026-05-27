from apps.knowledge.models import QuestionHistory


def sidebar_history(request):
    data = {}

    qs = QuestionHistory.objects.order_by("-created_at")[:5]

    for q in qs:
        data.setdefault(q.theme, []).append(q.question)

    return {
        "historique_questions": data
    }
