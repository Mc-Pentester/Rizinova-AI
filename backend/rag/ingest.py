import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

# Charger .env
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")

if not PINECONE_API_KEY or not PINECONE_INDEX_NAME:
    raise ValueError("PINECONE_API_KEY ou PINECONE_INDEX_NAME manquant dans .env")

try:
    # Import relative fix - ajout du dossier parent au path
    current_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(current_dir))
    from embedder import embed_text
except ImportError as e:
    print(f"❌ Erreur d'import : {e}")
    sys.exit(1)

# Créer le client Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
except Exception as e:
    print(f"❌ Erreur connexion Pinecone : {e}")
    sys.exit(1)

# Créer l'index si inexistant
try:
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"📦 Création de l'index '{PINECONE_INDEX_NAME}'...")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=1536,  # embeddings OpenAI
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV)
        )
        print(f"✅ Index '{PINECONE_INDEX_NAME}' créé")
except Exception as e:
    print(f"❌ Erreur création index : {e}")
    sys.exit(1)

index = pc.Index(PINECONE_INDEX_NAME)

# Chemin du fichier JSON
BASE_DIR = Path(__file__).resolve().parent
json_path = BASE_DIR / "riz_knowledge.json"

# Charger les documents
try:
    with open(json_path, "r", encoding="utf-8") as f:
        documents = json.load(f)
    print(f"✅ {len(documents)} documents chargés")
except FileNotFoundError:
    print(f"❌ Fichier non trouvé : {json_path}")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"❌ Erreur décodage JSON : {e}")
    sys.exit(1)

vectors = []

# Générer les embeddings avec gestion d'erreur
try:
    for idx, doc in enumerate(documents):
        try:
            embedding = embed_text(doc["content"])
            vectors.append({
                "id": doc.get("id", str(idx)),
                "values": embedding,
                "metadata": {
                    "title": doc.get("title", ""),
                    "category": doc.get("category", ""),
                    "culture": doc.get("culture", ""),
                    "region": doc.get("region", ""),
                    "difficulty": doc.get("difficulty", ""),
                    "content": doc.get("content", "")[:512]  # Limiter le contenu stocké
                }
            })
            if (idx + 1) % 10 == 0:
                print(f"   {idx + 1}/{len(documents)} documents traités...")
        except Exception as e:
            print(f"⚠️ Erreur pour document {idx}: {e}")
            continue
except Exception as e:
    print(f"❌ Erreur traitement embeddings : {e}")
    sys.exit(1)

# Envoyer dans Pinecone avec batch
try:
    BATCH_SIZE = 100
    for i in range(0, len(vectors), BATCH_SIZE):
        batch = vectors[i:i+BATCH_SIZE]
        index.upsert(vectors=batch)
        print(f"   Batch {i//BATCH_SIZE + 1} envoyé ({len(batch)} documents)")
    print(f"✅ {len(vectors)} documents ingérés avec succès dans Pinecone")
except Exception as e:
    print(f"❌ Erreur envoi à Pinecone : {e}")
    sys.exit(1)
