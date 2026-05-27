from ..models import ConsultantSession

class ConversationMemory:

    def get_history(self, user, session_id, limit=10):
        messages = ConsultantSession.objects.filter(
            user=user,
            session_id=session_id
        ).order_by("-created_at")[:limit]

        return list(reversed(messages))

    def save_message(self, user, session_id, role, message):
        ConsultantSession.objects.create(
            user=user,
            session_id=session_id,
            role=role,
            message=message
        )