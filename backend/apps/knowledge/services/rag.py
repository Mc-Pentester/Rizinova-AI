import os
from openai import OpenAI
from pinecone import Pinecone
from .embeddings import embed_text_cached
from apps.knowledge.models import QuestionHistory
from .pinecone_service import feed_database_from_pinecone
from .llm_service import openai_chat

# ───────────────────────────────
# 🔧 CONFIG
# ───────────────────────────────
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

TOP_K = int(os.getenv("RAG_TOP_K", 5))
MIN_SCORE = 0.80
MIN_DOCS = 2

# ───────────────────────────────
# 🧠 HISTORIQUE
# ───────────────────────────────
def detect_category(question: str) -> str:
    q = question.lower()
    if any(k in q for k in ["engrais", "fertilisation"]):
        return "Fertilisation"
    if any(k in q for k in ["maladie", "champignon"]):
        return "Maladies"
    if any(k in q for k in ["eau", "irrigation"]):
        return "Irrigation"
    if "récolte" in q:
        return "Récolte"
    if "stockage" in q:
        return "Stockage"
    return "Général"

def save_question(question: str):
    QuestionHistory.objects.create(
        question=question,
        theme=detect_category(question)
    )

# ───────────────────────────────
# 🤖 RAG PRINCIPAL
# ───────────────────────────────
def get_rag_answer(question: str):
    """
    Pipeline RAG principal utilisé par l'API
    """
    save_question(question)

    # 1️⃣ Recherche Pinecone
    results = query_pinecone(question, top_k=TOP_K)
    strong_docs = [r for r in results if r["score"] >= MIN_SCORE]

    # 🟢 Cas 1 : Pinecone suffisant
    if len(strong_docs) >= MIN_DOCS:
        return build_answer_from_docs(question, strong_docs)

    # 🔴 Cas 2 : fallback OpenAI
    answer = call_openai_llm(question, results)
    return answer, [d["metadata"].get("title", "") for d in results]

def build_answer_from_docs(question, docs):
    """
    Génère une réponse uniquement à partir des documents Pinecone
    """
    context = "\n\n".join(d["metadata"]["content"] for d in docs)

    prompt = f"""
Tu es RiziNova AI, expert en riziculture.

CONTEXTE:
{context}

QUESTION:
{question}

Réponds de manière claire, pratique et concise.
"""
    # Utiliser OpenAI si dispo, sinon renvoyer juste le contexte
    try:
        answer = openai_chat(prompt)
    except Exception:
        # fallback simple
        answer = f"Documents disponibles:\n{context}"

    sources = [d["metadata"].get("title", "") for d in docs]
    return answer, sources

def call_openai_llm(question, docs):
    """
    Appel OpenAI pour fallback quand Pinecone seul n'est pas suffisant
    """
    context = "\n\n".join(d["metadata"]["content"] for d in docs)
    prompt = f"""
Tu es RiziNova AI, expert agricole.

CONTEXTE:
{context}

QUESTION:
{question}

Réponds clairement et avec des conseils pratiques.
"""
    return openai_chat(prompt)

# ───────────────────────────────
# ⚡ FALLBACK PINECONE
# ───────────────────────────────
def query_pinecone_fallback(question, top_k=TOP_K):
    """
    Utilisé si OpenAI est indisponible.
    """
    results = query_pinecone(question, top_k=top_k)
    strong_docs = [r for r in results if r["score"] >= 0.5]
    return strong_docs
