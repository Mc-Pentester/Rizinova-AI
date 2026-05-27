import os
import sys
import django
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# =============================
# CONFIG
# =============================
DJANGO_SETTINGS = "config.settings"   # ⚠ adapte si différent
BATCH_SIZE = 64
INDEX_FILENAME = "faiss_ivf.index"

# =============================
# INIT DJANGO PROPREMENT
# =============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)
django.setup()

from apps.knowledge.models import KnowledgeDocument

# =============================
# LOAD DOCUMENTS
# =============================
print("Loading documents from DB...")

documents = list(
    KnowledgeDocument.objects.only("id", "title", "content")
)

if not documents:
    print("❌ No documents found.")
    sys.exit(1)

print(f"✅ {len(documents)} documents loaded.")

# =============================
# LOAD MODEL
# =============================
print("Loading embedding model...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Model ready.")

# =============================
# ENCODE BY BATCH
# =============================
all_embeddings = []

for i in range(0, len(documents), BATCH_SIZE):
    batch = documents[i:i+BATCH_SIZE]
    texts = [
        f"{doc.title or ''} {doc.content}"
        for doc in batch
    ]

    print(f"Encoding {i} → {i+len(batch)}")
    emb = model.encode(texts, batch_size=BATCH_SIZE)
    all_embeddings.append(emb.astype("float32"))

embeddings = np.vstack(all_embeddings)
faiss.normalize_L2(embeddings)

print("Embeddings ready.")

# =============================
# BUILD INDEX
# =============================
dim = embeddings.shape[1]
total_docs = len(documents)

# Correction FAISS : FlatIP si moins de 20 000 documents pour garantir performance et exactitude sans crash
if total_docs < 20000:
    print("Using FlatIP index (Exact search, highly recommended for local deployment)")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
else:
    print("Using IVF index for scale...")
    nlist = int(np.sqrt(total_docs))
    
    # Sécurité d'entraînement : FAISS requiert min 39 points par centroïde pour s'entraîner correctement
    min_points = 39 * nlist
    if total_docs < min_points:
        nlist = max(1, total_docs // 39)
        print(f"Adjusted nlist to {nlist} to satisfy FAISS training constraints.")
        
    quantizer = faiss.IndexFlatIP(dim)
    index = faiss.IndexIVFFlat(
        quantizer,
        dim,
        nlist,
        faiss.METRIC_INNER_PRODUCT
    )
    print("Training IVF...")
    index.train(embeddings)
    index.add(embeddings)

# =============================
# SAVE INDEX
# =============================
index_path = os.path.join(BASE_DIR, INDEX_FILENAME)
faiss.write_index(index, index_path)
print(f"✅ INDEX créé avec succès → {index_path}")