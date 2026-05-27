from apps.knowledge.models import CachedAnswer
from django.utils import timezone
from datetime import timedelta


CACHE_TTL_HOURS = 24  # modifiable


def get_cached_answer(question: str):
    q_hash = CachedAnswer.hash_question(question)

    try:
        cached = CachedAnswer.objects.get(question_hash=q_hash)

        # Vérifier expiration
        if timezone.now() - cached.created_at < timedelta(hours=CACHE_TTL_HOURS):
            return cached.answer
        else:
            cached.delete()

    except CachedAnswer.DoesNotExist:
        return None


def save_cached_answer(question: str, answer: str):
    q_hash = CachedAnswer.hash_question(question)

    CachedAnswer.objects.update_or_create(
        question_hash=q_hash,
        defaults={
            "question": question,
            "answer": answer,
            "created_at": timezone.now()
        }
    )
