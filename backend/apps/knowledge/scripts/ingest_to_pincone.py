import os
import pinecone
from openai import OpenAI
from django.conf import settings
import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.knowledge.models import KnowledgeDocument

# 🔑 OpenAI
client = OpenAI(api_key=settings.OPENAI_API_KEY)

# 🔑 Pinecone
pinecone.init(api_key="YOUR_PINECONE_KEY", environment="us-east1-gcp")
index_name = "rizinova"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(index_name, dimension=1536, metric="cosine")
index = pinecone.Index(index_name)

# Ingestion
for doc in KnowledgeDocument.objects.all():
    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=doc.content
    ).data[0].embedding
    
    index.upsert([
        {
            "id": str(doc.id),
            "values": embedding,
            "metadata": {
                "title": doc.title,
                "theme": doc.theme,
                "content": doc.content
            }
        }
    ])
    print(f"Document ingéré : {doc.title}")
