from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from apps.knowledge.rag_service import get_rag_answer_async
from apps.knowledge.services.cache_service import get_cached_answer, save_cached_answer
from .models import Conversation, Message


# 🌐 Pages Web
def compte(request):
    return render(request, "compte.html")


def chat_page(request):
    return render(request, "chat.html")


@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        question = request.data.get("question", "").strip()

        if not question:
            return Response(
                {"error": "Question requise"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1️⃣ Vérifier cache
        cached_answer = get_cached_answer(question)
        if cached_answer:
            return Response({
                "answer": cached_answer,
                "sources": [],
                "source": "cache"
            })

        try:
            # 2️⃣ RAG LOCAL (sync)
            answer = get_rag_answer_async(question)
            sources = []  # Pour l'instant vide, tu peux ajouter les docs pertinents plus tard

        except Exception as e:
            return Response(
                {"error": f"Erreur RAG: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 3️⃣ Sauvegarder cache
        if answer:
            save_cached_answer(question, answer)

        # 4️⃣ Sauvegarde DB
        conversation = Conversation.objects.create()

        Message.objects.create(
            conversation=conversation,
            content=question,
            is_user=True
        )

        Message.objects.create(
            conversation=conversation,
            content=answer,
            is_user=False
        )

        # 5️⃣ Réponse API
        answer, sources = get_rag_answer_async(question)
        return Response({
            "conversation_id": conversation.id,
            "answer": answer,
            "sources": sources,
            "source": "rag"
        })
