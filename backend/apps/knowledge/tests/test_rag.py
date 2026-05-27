# test_rag.py
# -*- coding: utf-8 -*-
import os
import django

# 1️⃣ Initialiser Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.knowledge.rag_service import get_rag_answer
from apps.knowledge.models import KnowledgeDocument

def test_rag():
    # 💬 Question à tester
    question = "Comment améliorer la production de riz irrigué en zone humide ?"

    # 🔹 Vérifier qu'il y a des documents
    if not KnowledgeDocument.objects.exists():
        print("⚠️ Aucun document dans la base KnowledgeDocument. Ajoutez-en pour tester.")
        return

    # 🔹 Appel RAG offline
    answer, sources = get_rag_answer(question)

    # 🔹 Affichage résultats
    print("=== QUESTION ===")
    print(question)
    print("\n=== REPONSE ===")
    print(answer)
    print("\n=== SOURCES ===")
    for s in sources:
        print("-", s)

if __name__ == "__main__":
    test_rag()
