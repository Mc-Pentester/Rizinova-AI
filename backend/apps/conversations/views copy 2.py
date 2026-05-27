# apps/knowledge/views.py

from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import FileResponse

from apps.knowledge.rag_service import get_rag_answer
from apps.knowledge.pdf_report_service import generate_b2b_pdf
from apps.knowledge.services.cache_service import get_cached_answer, save_cached_answer
from apps.knowledge.services.quota_service import check_user_quota
from .models import Conversation, Message


# ------------------------------
# Pages classiques
# ------------------------------
def compte(request):
    return render(request, "compte.html")


def chat_page(request):
    return render(request, "chat.html")


# ------------------------------
# API Chat + PDF B2B
# ------------------------------
@method_decorator(csrf_exempt, name="dispatch")
class ChatAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        question = data.get("question", "").strip()
        country = data.get("country")
        region = data.get("region")
        variety = data.get("variety")
        doc_type = data.get("doc_type")
        farm_data = data.get("farm_data", {})
        return_pdf = data.get("pdf", False)

        if not question:
            return Response({"error": "Question requise"}, status=400)

        user_id = (
            str(request.user.id)
            if request.user.is_authenticated
            else request.META.get("REMOTE_ADDR", "anonymous")
        )

        plan = getattr(request.user, "plan", "free")

        # ---------- QUOTA ----------
        if request.user.is_authenticated:
            allowed = check_user_quota(request.user)
            if not allowed:
                return Response({"error": "Limite quotidienne atteinte"}, status=403)

        # ---------- CACHE ----------
        cached_answer = get_cached_answer(question)
        if cached_answer and not return_pdf:
            return Response({
                "answer": cached_answer,
                "sources": [],
                "source": "cache",
                "confidence_score": None
            })

        # ---------- RAG ----------
        try:
            rag_result = get_rag_answer(
                user_id=user_id,
                query=question,
                plan=plan
            )
            report_answer = rag_result.get("answer", "")
            sources = rag_result.get("sources", [])
            confidence_score = rag_result.get("confidence_score", None)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({"error": f"Erreur interne: {str(e)}"}, status=500)

        # ---------- Sauvegarde cache ----------
        if not return_pdf:
            save_cached_answer(question, report_answer)

        # ---------- Sauvegarde conversation ----------
        conversation = Conversation.objects.create(
            user=request.user if request.user.is_authenticated else None
        )

        Message.objects.create(
            conversation=conversation,
            content=question,
            is_user=True
        )

        Message.objects.create(
            conversation=conversation,
            content=report_answer,
            is_user=False
        )

        # ---------- Retour ----------
        if return_pdf:
            pdf_path = generate_b2b_pdf(
                user_id=user_id,
                query=question,
                farm_data=farm_data,
                country=country,
                region=region,
                variety=variety,
                doc_type=doc_type,
                plan=plan
            )
            return FileResponse(open(pdf_path, "rb"), as_attachment=True, filename="b2b_report.pdf")
        else:
            return Response({
                "conversation_id": conversation.id,
                "answer": report_answer,
                "sources": sources,
                "confidence_score": confidence_score,
                "source": "rag"
            })