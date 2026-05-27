from apps.knowledge.services.rag import get_random_quick_tips

def quick_tips(request):
    return {
        "quick_tips": get_random_quick_tips(3)
    }
