# build_faiss_index.py
import os
import sys
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# =======================
from apps.knowledge.models import KnowledgeDocument

# =======================
# ⚙️ Config
# =======================
BATCH_SIZE = 100
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "faiss_ivf.index")
TOP_K = 5
RERANK_TOP_K = 8
MIN_SCORE = 0.3
ALPHA = 0.65
NPROBE_PERCENT = 0.1

# =======================
# 🔧 Load model
# =======================
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# =======================
# 🔧 Read documents in batches
# =======================
docs = KnowledgeDocument.objects.only("id", "title", "content")
doc_texts = []
for i, doc in enumerate(docs):
    text = f"{doc.title or ''} {doc.content}"
    doc_texts.append(text)
    if i % 100 == 0:
        print(f"Loaded {i} documents")

if not doc_texts:
    print("❌ No documents found in DB")
    sys.exit(1)

# =======================
# 🔧 Encode embeddings batch by batch
# =======================
all_embeddings = []
for start in range(0, len(doc_texts), BATCH_SIZE):
    batch = doc_texts[start : start + BATCH_SIZE]
    print(f"Encoding batch {start} -> {start + len(batch)}")
    emb = model.encode(batch, batch_size=BATCH_SIZE)
    all_embeddings.append(emb.astype("float32"))

embeddings = np.vstack(all_embeddings)
faiss.normalize_L2(embeddings)
dim = embeddings.shape[1]

# =======================
# 🔧 Build FAISS index
# =======================
if len(doc_texts) < 5000:
    print("Using IndexFlatIP")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
else:
    print("Using IndexIVFFlat")
    nlist = int(np.sqrt(len(doc_texts)))
    quantizer = faiss.IndexFlatIP(dim)
    index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
    print("Training index...")
    index.train(embeddings)
    index.add(embeddings)

# =======================
# 🔧 Save index
# =======================
faiss.write_index(index, FAISS_INDEX_PATH)
print(f"✅ FAISS index built successfully at {FAISS_INDEX_PATH}")