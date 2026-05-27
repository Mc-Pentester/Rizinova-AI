from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.knowledge.rag_service import get_rag_answer
from .models import Conversation, Message


# 🌐 PAGE WEB
def compte(request):
    return render(request, "compte.html")

def chat_page(request):
    return render(request, "chat.html")


# 🔌 API CHAT (POST)
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

        # 🔹 RAG
        answer, sources = get_rag_answer(question)

        # 🔹 DB
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

        return Response({
            "conversation_id": conversation.id,
            "answer": answer,
            "sources": sources
        })
