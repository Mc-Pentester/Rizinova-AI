#from pinecone import Pinecone
from apps.knowledge.models import KnowledgeDocument
from .embeddings import embed_text_cached

#pc = Pinecone(api_key=settings.PINECONE_API_KEY)
#index = pc.Index(settings.PINECONE_INDEX_NAME)

def index_documents():
    docs = KnowledgeDocument.objects.all()

    vectors = []
    for doc in docs:
        vectors.append({
            "id": str(doc.id),
            "values": embed_text_cached(doc.content),
            "metadata": {
                "title": doc.title,
                "theme": doc.theme,
                "region": doc.region,
                "content": doc.content
            }
        })

    if vectors:
        index.upsert(vectors=vectors)
