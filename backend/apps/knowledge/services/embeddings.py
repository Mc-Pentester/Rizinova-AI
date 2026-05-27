import os
import hashlib
from openai import OpenAI
from django.core.cache import cache

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
EMBED_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

EMBED_TTL = 60 * 60 * 24 * 30  # 30 jours

def _make_cache_key(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return f"emb:{h}"

def embed_text_cached(text: str) -> list:
    """
    Génère un embedding OpenAI avec cache Django
    """
    cache_key = _make_cache_key(text)
    cached = cache.get(cache_key)

    if cached is not None:
        return cached

    embedding = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    ).data[0].embedding

    cache.set(cache_key, embedding, timeout=EMBED_TTL)
    return embedding
