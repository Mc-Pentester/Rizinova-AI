# apps/knowledge/embeddings.py

import threading
import numpy as np
from functools import lru_cache
from sentence_transformers import SentenceTransformer
import faiss


# ==========================================================
# 🌍 CONFIGURATION SAAS INTERNATIONAL
# ==========================================================

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# ==========================================================
# 🔒 THREAD SAFE GLOBAL
# ==========================================================

_model = None
_lock = threading.Lock()


# ==========================================================
# 🧠 LAZY LOAD MODEL (ANTI-SATURATION)
# ==========================================================

def get_model():
    """
    Charge le modèle uniquement à la première utilisation.
    Thread-safe pour production SaaS.
    """
    global _model

    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer(MODEL_NAME)

    return _model


# ==========================================================
# ⚡ EMBEDDING AVEC CACHE
# ==========================================================

@lru_cache(maxsize=2000)
def embed_text_cached(text: str) -> np.ndarray:
    """
    Embedding avec cache LRU.
    Évite recalcul pour requêtes fréquentes.
    """
    model = get_model()
    vec = model.encode(text).astype("float32")
    return vec


def embed_text(text: str, normalize: bool = True) -> np.ndarray:
    """
    Retourne embedding numpy optimisé FAISS.

    Args:
        text (str)
        normalize (bool): normalisation L2 (recommandé pour FAISS)

    Returns:
        np.ndarray
    """
    vec = embed_text_cached(text)

    if normalize:
        vec = vec.reshape(1, -1)
        faiss.normalize_L2(vec)
        return vec[0]

    return vec


# ==========================================================
# 📦 BATCH EMBEDDING (BUILD INDEX)
# ==========================================================

def embed_batch(texts: list, normalize: bool = True) -> np.ndarray:
    """
    Encode une liste de textes (plus efficace que boucle).
    Utilisé pour construire FAISS index.
    """
    model = get_model()

    vectors = model.encode(texts).astype("float32")

    if normalize:
        faiss.normalize_L2(vectors)

    return vectors


# ==========================================================
# 🔎 COSINE SIMILARITY SAFE
# ==========================================================

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Similarité cosine robuste.
    Protège contre division par zéro.
    """
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(np.dot(a, b) / (norm_a * norm_b))


# ==========================================================
# 🧪 TEST LOCAL
# ==========================================================

if __name__ == "__main__":

    text1 = "Rice irrigation in tropical climate"
    text2 = "Wetland rice production techniques"
    text3 = "Poultry farming in rural areas"

    emb1 = embed_text(text1)
    emb2 = embed_text(text2)
    emb3 = embed_text(text3)

    print("rice vs rice:", cosine_similarity(emb1, emb2))
    print("rice vs poultry:", cosine_similarity(emb1, emb3))
    