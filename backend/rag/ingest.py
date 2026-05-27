import json
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
from embedder import embed_text

# Charger .env
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise ValueError("PINECONE_API_KEY ou PINECONE_INDEX_NAME manquant dans .env")

# Créer le client Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

# Créer l'index si inexistant
if PINECONE_INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=PINECONE_INDEX_NAME,
        dimension=1536,  # embeddings OpenAI
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
    )

index = pc.Index(PINECONE_INDEX_NAME)

# Chemin du fichier JSON
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "riz_knowledge.json")

# Charger les documents
with open(json_path, "r", encoding="utf-8") as f:
    documents = json.load(f)

vectors = []

for doc in documents:
    embedding = embed_text(doc["content"])

    vectors.append({
        "id": doc["id"],
        "values": embedding,
        "metadata": {
            "title": doc["title"],
            "category": doc["category"],
            "culture": doc["culture"],
            "region": doc["region"],
            "difficulty": doc["difficulty"],
            "content": doc["content"]
        }
    })

# Envoyer dans Pinecone
index.upsert(vectors=vectors)

print(f"✅ {len(vectors)} documents ingérés avec succès")
