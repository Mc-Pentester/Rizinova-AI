from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from apps.knowledge.services.cache_service import get_cached_answer, save_cached_answer
from apps.knowledge.rag_service import get_rag_answer, retrieve_local_documents, query_pinecone

from .models import Conversation, Message

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
            return Response({"error": "Question requise"}, status=status.HTTP_400_BAD_REQUEST)

        # 1️⃣ Vérifier le cache
        cached_answer = get_cached_answer(question)
        if cached_answer:
            return Response({"answer": cached_answer, "source": "cache"})

        # 2️⃣ RAG avec fallback
        try:
            answer, sources = get_rag_answer(question)
        except Exception:
            # Fallback brut local + Pinecone
            local_docs = retrieve_local_documents(question)
            pinecone_docs = query_pinecone(question)
            all_docs = []

            if local_docs:
                all_docs.extend([{"content": d.content, "title": d.title} for d in local_docs])
            if pinecone_docs:
                all_docs.extend(pinecone_docs)

            if all_docs:
                seen = set()
                unique_docs = []
                for d in all_docs:
                    if d["content"] not in seen:
                        seen.add(d["content"])
                        unique_docs.append(d)

                answer = "\n\n".join(d["content"] for d in unique_docs)
                sources = [d["title"] for d in unique_docs]
            else:
                answer = "Impossible de générer une réponse pour le moment (aucun document pertinent)."
                sources = []

        # 3️⃣ Sauvegarde cache et DB
        if answer:
            save_cached_answer(question, answer)
        conversation = Conversation.objects.create()
        Message.objects.create(conversation=conversation, content=question, is_user=True)
        Message.objects.create(conversation=conversation, content=answer, is_user=False)

        return Response({
            "conversation_id": conversation.id,
            "answer": answer,
            "sources": sources,
            "source": "rag" if any("OpenAI" in s for s in sources) else "fallback"
        })
