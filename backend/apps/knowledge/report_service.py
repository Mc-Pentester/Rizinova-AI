# apps/knowledge/report_service.py
import os
import numpy as np
import faiss
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
from apps.knowledge.models import KnowledgeDocument

# ------------------------------
# CONFIGURATION
# ------------------------------
TOP_K = 5
RERANK_TOP_K = 8
MIN_SCORE = 0.3
ALPHA = 0.65
NPROBE_PERCENT = 0.1
FAISS_INDEX_PATH = "faiss_ivf.index"

_model = None
_faiss_index = None
_documents = []
_bm25 = None
_tokenized_corpus = []

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    return _model

def load_index():
    global _faiss_index, _documents, _bm25, _tokenized_corpus
    if _faiss_index is not None:
        return

    _faiss_index = faiss.read_index(FAISS_INDEX_PATH)
    _documents = list(KnowledgeDocument.objects.all())
    _tokenized_corpus = [
        f"{doc.title or ''} {doc.content}".lower().split() for doc in _documents
    ]
    _bm25 = BM25Okapi(_tokenized_corpus)

def embed_query(query):
    model = get_model()
    vec = model.encode(query).astype("float32")
    faiss.normalize_L2(vec.reshape(1, -1))
    return vec

# ------------------------------
# HYBRID SEARCH
# ------------------------------
def hybrid_search(query):
    load_index()
    if not _documents:
        return []

    q_vec = embed_query(query).reshape(1, -1)
    if isinstance(_faiss_index, faiss.IndexIVFFlat):
        _faiss_index.nprobe = max(1, int(_faiss_index.nlist * NPROBE_PERCENT))
    D, I = _faiss_index.search(q_vec, RERANK_TOP_K)

    vector_scores = {idx: float(score) for score, idx in zip(D[0], I[0]) if idx != -1}
    bm25_scores = _bm25.get_scores(query.lower().split())

    results = []
    for idx in range(len(_documents)):
        sem = vector_scores.get(idx, 0)
        lex = bm25_scores[idx]
        score = ALPHA * sem + (1 - ALPHA) * lex
        if score > MIN_SCORE:
            results.append((score, idx))
    results.sort(reverse=True)
    return results[:TOP_K]

# ------------------------------
# MULTI-CHUNKS + INDICATEURS
# ------------------------------
def get_expert_report(user_id, query, farm_data=None, country=None, region=None,
                      variety=None, doc_type=None, plan="free"):
    """
    Retourne un dict complet avec :
    - rag_chunks : contenu multi-chunks
    - sources : titres documents
    - agronomy_risk : indicateurs agronomiques
    - financials : ROI, revenu attendu, coût
    """
    farm_data = farm_data or {}
    results = hybrid_search(query)

    rag_chunks = []
    sources = []
    max_chars = 1000 if plan == "free" else 3000
    context = ""

    for score, idx in results:
        doc = _documents[idx]
        sources.append(doc.title or str(doc.id))
        if len(context) + len(doc.content) > max_chars:
            break
        context += doc.content + " "
        rag_chunks.append(doc.content)

    # ------------------
    # INDICATEURS AGRONOMIQUES
    # ------------------
    area = farm_data.get("area_ha", 1)
    expected_yield = farm_data.get("expected_yield_ton", 3)
    historical_yield = farm_data.get("historical_yield", expected_yield)
    agronomy_risk = {
        "yield_gap": max(0, expected_yield - historical_yield),
        "recommendation": "Optimiser fertilisation et densité de semis"  # exemple
    }

    # ------------------
    # INDICATEURS FINANCIERS
    # ------------------
    cost = farm_data.get("cost_per_ha", 0) * area
    revenue = farm_data.get("price_per_ton", 0) * expected_yield * area
    roi = (revenue - cost) / cost if cost > 0 else None
    financials = {
        "cost_total": cost,
        "revenue_total": revenue,
        "roi": roi
    }

    return {
        "rag_chunks": rag_chunks,
        "sources": sources,
        "agronomy_risk": agronomy_risk,
        "financials": financials
    }