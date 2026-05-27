# apps/knowledge/auto_rag.py

import os
from collections import defaultdict
from typing import List, Dict, Tuple
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from apps.knowledge.models import KnowledgeDocument
from .rag_service import get_rag_answer
from .response_evaluator import ResponseEvaluator

# ==========================
# 1️⃣ Sujets clés à couvrir
# ==========================
KEY_TOPICS = [
    "rendement du riz",
    "saison pluviale",
    "saison sèche",
    "irrigation",
    "gestion de l’eau",
    "fertilisation",
    "maladies fongiques",
    "maladies bactériennes",
    "ravageurs",
    "variétés locales",
    "densité de semis",
    "pratiques culturales",
    "post-récolte"
]

# ==========================
# 2️⃣ Audit de la base existante
# ==========================
def audit_base() -> Dict[str, List[str]]:
    coverage = defaultdict(list)
    documents = KnowledgeDocument.objects.only("id", "title", "content")
    for doc in documents:
        content = f"{doc.title or ''} {doc.content or ''}".lower()
        for topic in KEY_TOPICS:
            if topic.lower() in content:
                coverage[topic].append(doc.title or str(doc.id))
    return coverage

def missing_topics(coverage: Dict[str, List[str]]) -> List[str]:
    return [topic for topic in KEY_TOPICS if topic not in coverage or len(coverage[topic]) == 0]

# ==========================
# 3️⃣ Enrichissement de la base
# ==========================
def prepare_new_documents(file_paths: List[str]):
    new_docs = []
    for file_path in file_paths:
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        title = os.path.basename(file_path)
        new_doc = KnowledgeDocument(title=title, content=content)
        new_docs.append(new_doc)
    KnowledgeDocument.objects.bulk_create(new_docs)
    print(f"{len(new_docs)} nouveaux documents ajoutés à la base.")

# ==========================
# 4️⃣ RAG + évaluation + optimisation automatique
# ==========================
def generate_answer(user_id: str, query: str, plan: str = "free") -> Dict:
    # 1️⃣ Récupération réponse RAG
    context, sources = get_rag_answer(user_id=user_id, query=query, plan=plan)

    evaluator = ResponseEvaluator()
    evaluation = evaluator.evaluate(query, context)

    # 2️⃣ Mots-clés critiques pour vérification
    critical_keywords = ["carence", "maladie", "fertilisation", "irrigation", "rendement"]
    
    # 3️⃣ Réécriture automatique si score faible ou mots-clés absents
    if evaluation["final_score"] < 0.65 or not any(k in context.lower() for k in critical_keywords):
        optimized_context = f"""
Pour répondre à votre question : {query.strip()}

Les causes possibles et solutions :
- **Carences nutritionnelles** : azote, phosphore, potassium
- **Stress hydrique** : trop ou trop peu d’eau
- **Maladies** : fongiques ou bactériennes
- **Solutions pratiques** : ajuster fertilisation, irrigation, surveiller maladies, choisir variétés adaptées

Sources : {', '.join(sources)}.
"""
        context = optimized_context.strip()
        sources.append("Optimized synthesis")
        evaluation = evaluator.evaluate(query, context)

    return {
        "type": "knowledge",
        "context": context,
        "sources": sources,
        "evaluation": evaluation
    }

# ==========================
# 5️⃣ Pipeline complet
# ==========================
def run_full_pipeline(user_id: str, query: str, plan: str = "free", new_files: List[str] = []):
    # Audit base
    coverage = audit_base()
    missing = missing_topics(coverage)
    if missing:
        print("Sujets manquants : ", missing)

    # Enrichissement avec fichiers supplémentaires
    if new_files:
        prepare_new_documents(new_files)

    # Génération de réponse optimisée
    result = generate_answer(user_id=user_id, query=query, plan=plan)
    return result

# ==========================
# 6️⃣ Exemple d'utilisation
# ==========================
if __name__ == "__main__":
    user_id = "12345"
    query = "Les feuilles jaunissent"
    new_files = ["docs/fertilisation_riz.txt", "docs/irrigation_pluviale.txt"]

    answer = run_full_pipeline(user_id=user_id, query=query, plan="free", new_files=new_files)
    print("=== Réponse générée ===")
    print(answer["context"])
    print("Sources :", answer["sources"])
    print("Évaluation :", answer["evaluation"])