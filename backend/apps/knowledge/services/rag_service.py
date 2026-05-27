import os
from pinecone import Pinecone
from .embeddings import embed_text_cached  # adapte si besoin
from openai import OpenAI

# 🔹 Config OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("RAG_MODEL", "gpt-3.5-turbo")
client = OpenAI(api_key=OPENAI_API_KEY)

# 🔹 Config Pinecone
TOP_K = int(os.getenv("RAG_TOP_K", 5))
MIN_SCORE = 0.80
MIN_DOCS = 2

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME"))

# ===============================
# 🔹 Fonctions Pinecone
# ===============================

def query_pinecone(question: str, top_k=TOP_K):
    embedding = embed_text_cached(question)
    res = index.query(vector=embedding, top_k=top_k, include_metadata=True)
    return [
        {"id": m.id, "score": m.score, "metadata": m.metadata}
        for m in res.matches
    ]

def query_pinecone_fallback(question: str):
    dummy_vector = [0.0] * 1536
    res = index.query(vector=dummy_vector, top_k=TOP_K, include_metadata=True)
    return [
        {"id": m.id, "score": m.score, "metadata": m.metadata}
        for m in res.matches
    ] if res.matches else []

def build_answer_from_docs(question, docs):
    context = "\n\n".join(d["metadata"]["content"] for d in docs)
    answer = f"Réponse basée sur les documents :\n{context}\n\nQuestion : {question}"
    sources = [d["metadata"].get("title", "Unknown") for d in docs]
    return answer, sources

# ===============================
# 🔹 Fonction principale RAG
# ===============================

def get_rag_answer(question: str):
    """
    Tente d'abord Pinecone, puis OpenAI si nécessaire.
    """
    results = query_pinecone(question, top_k=TOP_K)

    # Cas 1 : Pinecone suffisant
    strong_docs = [r for r in results if r["score"] >= MIN_SCORE]
    if len(strong_docs) >= MIN_DOCS:
        return build_answer_from_docs(question, strong_docs)

    # Cas 2 : Pinecone insuffisant → OpenAI
    context = "\n\n".join(d["metadata"]["content"] for d in results)
    prompt = f"""
Tu es un expert agricole spécialisé dans le riz.
Réponds de manière pratique, claire et fiable.

CONTEXTE:
{context}

QUESTION:
{question}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=350
        )
        answer = response.choices[0].message.content
        sources = [m["metadata"]["title"] for m in results]
        return answer, sources

    except Exception:
        # Fallback Pinecone si OpenAI échoue
        fallback_docs = query_pinecone_fallback(question)
        if fallback_docs:
            answer, sources = build_answer_from_docs(question, fallback_docs)
            sources.append("pinecone-only (OpenAI indisponible)")
            return answer, sources
        else:
            return "Impossible de générer une réponse pour le moment (OpenAI indisponible et aucun document pertinent).", []
