import os
import sys
import re
from pathlib import Path
from tqdm import tqdm
from difflib import SequenceMatcher
import fitz
import django
import numpy as np
from sentence_transformers import SentenceTransformer
from django.db import transaction
from concurrent.futures import ThreadPoolExecutor, as_completed

# ----------------------------
# INITIALISATION DJANGO
# ----------------------------
PROJECT_ROOT = r"C:\rizinova_offline_1.1\backend"
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.knowledge.models import KnowledgeDocument

# ----------------------------
# CONFIGURATION
# ----------------------------
PDF_ROOT_FOLDER = r"C:\rizinova_offline_1.1\backend\docs"
CHUNK_MAX_TOKENS = 300
DEDUP_THRESHOLD = 0.85
DEFAULT_THEME = "général"
CLEAN_BASE = True
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
MAX_WORKERS_PDF = 4
MAX_WORKERS_CHUNK = 8

# ----------------------------
# INIT EMBEDDING
# ----------------------------
model = SentenceTransformer(EMBEDDING_MODEL)
global_chunk_counter = 1

# ----------------------------
# UTILITAIRES
# ----------------------------
def extract_clean_text_from_pdf(pdf_path: str) -> str:
    text_pages = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Impossible d’ouvrir {pdf_path}: {e}")
        return ""
    for page_num, page in enumerate(doc):
        try:
            text = page.get_text()
            text = re.sub(r'\n{2,}', '\n', text)
            text = re.sub(r'Page\s+\d+', '', text, flags=re.IGNORECASE)
            text_pages.append(text.strip())
        except Exception as e:
            print(f"⚠️ Erreur page {page_num+1} dans {pdf_path}: {e}")
    doc.close()
    return re.sub(r'\s+', ' ', "\n".join(text_pages)).strip()

def split_text_by_tokens(text: str, max_tokens=CHUNK_MAX_TOKENS):
    words = text.split()
    chunks, buffer = [], []
    for word in words:
        buffer.append(word)
        if len(buffer) >= max_tokens:
            chunks.append(" ".join(buffer))
            buffer = []
    if buffer:
        chunks.append(" ".join(buffer))
    return chunks

def deduplicate_docs(docs):
    unique = []
    for d in docs:
        if all(SequenceMatcher(None, d['content'], u['content']).ratio() < DEDUP_THRESHOLD for u in unique):
            unique.append(d)
    return unique

def encode_chunk(chunk: str) -> list:
    return model.encode(chunk).astype("float32").tolist()

def enrich_chunks_parallel(chunks, source, theme, country):
    global global_chunk_counter
    documents = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_CHUNK) as executor:
        futures = {executor.submit(encode_chunk, c): i for i, c in enumerate(chunks)}
        for future in as_completed(futures):
            i = futures[future]
            try:
                embedding = future.result()
            except Exception as e:
                print(f"⚠️ Erreur embedding chunk {i+1} : {e}")
                embedding = []
            chunk_text = chunks[i]
            summary = chunk_text[:200]
            title = f"Chunk #{global_chunk_counter} ({source} – partie {i+1})"
            documents.append({
                "title": title,
                "content": chunk_text,
                "embedding": embedding,
                "metadata": {
                    "source": source,
                    "theme": theme,
                    "country": country,
                    "summary": summary
                },
                "theme": theme,
                "summary": summary
            })
            global_chunk_counter += 1
    return documents

def save_to_local_db(documents):
    objs = []
    for doc in documents:
        if not KnowledgeDocument.objects.filter(title=doc["title"], region=doc["metadata"]["country"]).exists():
            objs.append(KnowledgeDocument(
                title=doc["title"],
                content=doc["content"],
                embedding=doc["embedding"],
                metadata=doc["metadata"],
                region=doc["metadata"]["country"],
                theme=doc["theme"],
                summary=doc["summary"]
            ))
    with transaction.atomic():
        KnowledgeDocument.objects.bulk_create(objs)
    return len(objs)

def pdf_to_rag_pro(pdf_path, theme=DEFAULT_THEME, country=None):
    source = Path(pdf_path).stem
    country = country or "Inconnu"
    text = extract_clean_text_from_pdf(pdf_path)
    if not text:
        print(f"⚠️ Aucun texte extrait pour {pdf_path}")
        return 0
    chunks = split_text_by_tokens(text)
    print(f"ℹ️ {len(chunks)} chunks générés pour {source} ({country})")
    docs = enrich_chunks_parallel(chunks, source, theme, country)
    docs = deduplicate_docs(docs)
    return save_to_local_db(docs)

def clean_knowledge_base():
    with transaction.atomic():
        deleted_count, _ = KnowledgeDocument.objects.all().delete()
        print(f"🧹 Base nettoyée : {deleted_count} documents supprimés.")

def process_country_pdfs(country_folder: Path):
    country_name = country_folder.name
    pdf_files = list(country_folder.glob("*.pdf"))
    total_chunks = 0
    for pdf_path in pdf_files:
        try:
            chunks_created = pdf_to_rag_pro(str(pdf_path), country=country_name)
            total_chunks += chunks_created
        except Exception as e:
            print(f"❌ Erreur traitement {pdf_path}: {e}")
    return country_name, len(pdf_files), total_chunks

# ----------------------------
# PROCESSUS GLOBAL + ANALYSE FINALE
# ----------------------------
def process_all_pdfs(root_folder=PDF_ROOT_FOLDER):
    if CLEAN_BASE:
        clean_knowledge_base()

    root = Path(root_folder)
    total_pdfs, total_chunks, errors = 0, 0, []
    summary_by_country = {}

    country_folders = [f for f in root.iterdir() if f.is_dir()]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS_PDF) as executor:
        futures = {executor.submit(process_country_pdfs, folder): folder for folder in country_folders}
        for future in tqdm(as_completed(futures), total=len(futures), desc="Indexation multi-thread PDF"):
            try:
                country_name, pdf_count, chunks_created = future.result()
                total_pdfs += pdf_count
                total_chunks += chunks_created
                summary_by_country[country_name] = {"pdfs": pdf_count, "chunks": chunks_created}
            except Exception as e:
                folder = futures[future]
                print(f"❌ Erreur traitement dossier {folder}: {e}")
                errors.append(str(folder))

    # Rapport final
    print("\n🎯 Rapport final :")
    print(f"📄 PDFs traités : {total_pdfs}")
    print(f"📝 Chunks créés : {total_chunks}")
    print(f"⚠️ Dossiers en erreur : {len(errors)}")
    if errors:
        for e in errors:
            print(f"   - {e}")

    print("\n📌 Analyse finale de la base de connaissance :")
    total_docs = KnowledgeDocument.objects.count()
    countries = KnowledgeDocument.objects.values_list("region", flat=True).distinct()
    avg_chunks_per_country = total_docs / len(countries) if countries else 0
    for country, info in summary_by_country.items():
        print(f"   - {country} : {info['pdfs']} PDFs → {info['chunks']} chunks")
    print(f"\n📝 Total chunks en base : {total_docs}")
    print(f"🌍 Nombre de pays/régions : {len(countries)}")
    print(f"📊 Moyenne de chunks par pays : {avg_chunks_per_country:.2f}")

# ----------------------------
# LANCEMENT
# ----------------------------
if __name__ == "__main__":
    process_all_pdfs()