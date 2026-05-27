# =========================================================
# RAG V7 — ASSISTANT AGRONOME LOCAL INTELLIGENT
# =========================================================

import os
import threading
from typing import List, Tuple
from collections import defaultdict

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from django.conf import settings
from apps.knowledge.models import KnowledgeDocument, ConversationMessage

# =========================================================
# CONFIGURATION
# =========================================================
TOP_K_FREE = 3
TOP_K_PRO = 5
ALPHA = 0.6
MIN_SCORE = 0.25
MAX_HISTORY = 5
CHUNK_SIZE = 200
SIM_THRESHOLD = 0.85  # seuil pour fusionner phrases similaires

FAISS_INDEX_PATH = os.path.join(settings.BASE_DIR, "faiss_ivf.index")

# =========================================================
# GLOBALS
# =========================================================
_model = None
_index = None
_phrases: List[str] = []
_phrase_docs: List[KnowledgeDocument] = []
_bm25 = None
_tokenized = []
_lock = threading.Lock()

# =========================================================
# 1️⃣ MODEL & EMBEDDINGS
# =========================================================
def get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

def embed(text: str):
    model = get_model()
    vec = model.encode(text).astype("float32")
    faiss.normalize_L2(vec.reshape(1, -1))
    return vec

# =========================================================
# 2️⃣ LOAD & INDEX PHRASES
# =========================================================
def split_into_phrases(text: str) -> List[str]:
    sentences = text.replace("\n", " ").split(". ")
    return [s.strip() for s in sentences if s.strip()]

def load_index():
    global _index, _phrases, _phrase_docs, _bm25, _tokenized
    if _index is not None:
        return

    with _lock:
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS index manquant : {FAISS_INDEX_PATH}")

        _index = faiss.read_index(FAISS_INDEX_PATH)
        docs = list(KnowledgeDocument.objects.only("id", "title", "content", "metadata"))

        for doc in docs:
            text = f"{doc.title or ''} {doc.content or ''}"
            for phrase in split_into_phrases(text):
                _phrases.append(phrase)
                _phrase_docs.append(doc)

        _tokenized = [p.lower().split() for p in _phrases]
        _bm25 = BM25Okapi(_tokenized)

# =========================================================
# 3️⃣ HYBRID SEARCH PHRASE-LEVEL
# =========================================================
def hybrid_search(query: str, top_k: int):
    load_index()
    q_vec = embed(query).reshape(1, -1)
    D, I = _index.search(q_vec, 20)

    vector_scores = {idx: 1 / (1 + dist) for dist, idx in zip(D[0], I[0]) if idx != -1}
    bm25_scores = _bm25.get_scores(query.lower().split())
    bm25_scores = bm25_scores / (np.max(bm25_scores) + 1e-6)

    results = []
    for idx in vector_scores:
        score = ALPHA * vector_scores[idx] + (1 - ALPHA) * bm25_scores[idx]
        if score > MIN_SCORE:
            results.append((score, idx))

    return sorted(results, reverse=True)[:top_k]

# =========================================================
# 4️⃣ SYNTHÈSE INTELLIGENTE AVEC SOURCES EXACTES
# =========================================================
def synthesize_with_sources(results: List[Tuple[float,int]], query: str) -> Tuple[str,List[str]]:
    if not results:
        return ("⚠️ Aucune information pertinente trouvée.", [])

    kept_phrases = []
    sources_set = set()
    embeddings = np.vstack([embed(_phrases[idx]) for _, idx in results])

    clustered = set()
    for i, (score_i, idx_i) in enumerate(results):
        if i in clustered:
            continue
        cluster_phrases = [_phrases[idx_i]]
        cluster_sources = {_phrase_docs[idx_i].id}
        clustered.add(i)
        for j, (score_j, idx_j) in enumerate(results[i+1:], start=i+1):
            if j in clustered:
                continue
            sim = cosine_similarity(embeddings[i].reshape(1,-1), embeddings[j].reshape(1,-1))[0][0]
            if sim >= SIM_THRESHOLD:
                cluster_phrases.append(_phrases[idx_j])
                cluster_sources.add(_phrase_docs[idx_j].id)
                clustered.add(j)
        kept_phrases.append(" ".join(cluster_phrases))
        sources_set.update(cluster_sources)

    # filtrer phrases non pertinentes par mots-clés query
    query_words = set(query.lower().split())
    final_phrases = []
    final_sources = set()
    for phrase in kept_phrases:
        if query_words & set(phrase.lower().split()):
            final_phrases.append(phrase)

    for src_id in sources_set:
        final_sources.add(src_id)

    if not final_phrases:
        return ("Je n'ai pas trouvé d'informations précises pour cette question.", [])

    # récupérer titres/documents des sources finales
    source_titles = []
    for doc in set(_phrase_docs[idx] for idx in range(len(_phrase_docs)) if _phrase_docs[idx].id in final_sources):
        if doc.title:
            source_titles.append(doc.title[:80])
        elif doc.metadata and "source" in doc.metadata:
            source_titles.append(doc.metadata["source"])
        else:
            source_titles.append("Guide riziculture local")

    return ("\n".join(final_phrases), source_titles)

# =========================================================
# 5️⃣ MÉMOIRE UTILISATEUR
# =========================================================
def get_clean_history(user_id: str):
    msgs = ConversationMessage.objects.filter(user_id=user_id).order_by("-created_at")[:MAX_HISTORY]
    return " | ".join([m.content for m in reversed(msgs)])

# =========================================================
# 6️⃣ FORMAT FINAL
# =========================================================
def format_response(answer: str, sources: List[str]) -> str:
    src_text = "\n".join([f"- {s}" for s in sources])
    return f"{answer}\n\n📚 Sources:\n{src_text}"

# =========================================================
# 7️⃣ MAIN RAG FUNCTION
# =========================================================
def get_rag_answer(user_id: str, query: str, plan: str="free") -> Tuple[str,List[str],float]:
    top_k = TOP_K_FREE if plan=="free" else TOP_K_PRO
    results = hybrid_search(query, top_k=top_k)
    answer, sources = synthesize_with_sources(results, query)

    history = get_clean_history(user_id)
    # enregistrer conversation
    ConversationMessage.objects.create(user_id=user_id, role="user", content=query)
    ConversationMessage.objects.create(user_id=user_id, role="assistant", content=answer)

    return format_response(answer, sources), sources, 0.9