import os
from apps.knowledge.models import KnowledgeDocument
from .embeddings import embed_text_cached  # adapte si besoin

try:
    import pinecone
except ImportError:
    pinecone = None

# ======================================================
# Lazy Pinecone
# ======================================================
def get_pinecone_index():
    if not pinecone:
        return None
    try:
        api_key = os.getenv("PINECONE_API_KEY")
        index_name = os.getenv("PINECONE_INDEX_NAME")
        if not api_key or not index_name:
            return None
        pinecone.init(api_key=api_key)
        return pinecone.Index(index_name)
    except Exception:
        # Hors réseau ou erreur Pinecone
        return None

# ======================================================
# Fonction pour alimenter la base locale
# ======================================================
def feed_database_from_pinecone(limit=5):
    """
    Alimente progressivement la base Django depuis Pinecone.
    Si Pinecone indisponible, rien ne plante.
    """

    index = get_pinecone_index()
    if not index:
        # Pinecone indisponible → fallback
        return 0

    # IDs déjà stockés localement
    existing_ids = set(
        KnowledgeDocument.objects.values_list("pinecone_id", flat=True)
    )

    # Requête Pinecone (dummy vector si nécessaire)
    try:
        results = index.query(
            vector=[0] * 1536,  # dummy vector
            top_k=limit,
            include_metadata=True
        )
    except Exception:
        return 0  # Pinecone indisponible → fallback

    created_count = 0

    for match in results.get("matches", []):
        pinecone_id = match["id"]

        if pinecone_id in existing_ids:
            continue

        meta = match.get("metadata", {})

        KnowledgeDocument.objects.create(
            pinecone_id=pinecone_id,
            title=meta.get("title", "Sans titre"),
            region=meta.get("region", "inconnue"),
            content=meta.get("content", ""),
            metadata=meta.get("metadata", {}),
        )

        created_count += 1

    return created_count
