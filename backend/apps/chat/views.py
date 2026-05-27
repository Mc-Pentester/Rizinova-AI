from rest_framework.decorators import api_view
from rest_framework.response import Response
from .rag import answer_with_rag

@api_view(["POST"])
def ask_bot(request):
    question = request.data.get("question", "").strip()

    if not question:
        return Response({"error": "Question vide"}, status=400)

    answer, sources = answer_with_rag(question)

    return Response({
        "question": question,
        "answer": answer,
        "sources": sources
    })
