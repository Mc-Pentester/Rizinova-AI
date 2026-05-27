import os
import sys
import re
from pathlib import Path
from tqdm import tqdm
from difflib import SequenceMatcher
import fitz
import django

# ----------------------------
# INITIALISATION DJANGO
# ----------------------------
PROJECT_ROOT = r"C:\rizinova_offline_1.1\backend"
sys.path.insert(0, PROJECT_ROOT)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.knowledge.models import KnowledgeDocument
from django.db import transaction

# ----------------------------
# CONFIGURATION
# ----------------------------
PDF_ROOT_FOLDER = r"C:\rizinova_offline_1.1\backend\docs"
CHUNK_MAX_LENGTH = 300
DEDUP_THRESHOLD = 0.85
DEFAULT_THEME = "général"
global_chunk_counter = 1  # compteur unique global
clean_base = True        # Nettoyer la base avant génération

# ----------------------------
# UTILITAIRES
# ----------------------------
def extract_clean_text_from_pdf(pdf_path: str) -> str:
    """
    Extrait le texte d'un PDF en ignorant les erreurs de polices.
    """
    text_pages = []
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ Impossible d’ouvrir {pdf_path}: {e}")
        return ""

    for page_num, page in enumerate(doc):
        try:
            page_text = page.get_text()
            page_text = re.sub(r'\n{2,}', '\n', page_text)
            page_text = re.sub(r'Page\s+\d+', '', page_text, flags=re.IGNORECASE)
            text_pages.append(page_text.strip())
        except Exception as e:
            print(f"⚠️ Erreur extraction page {page_num+1} dans {pdf_path}: {e}")

    doc.close()
    full_text = "\n".join(text_pages)
    full_text = re.sub(r'\s+', ' ', full_text).strip()
    return full_text

def split_text_smart(text: str):
    """
    Découpe le texte en chunks de taille CHUNK_MAX_LENGTH.
    Split par phrases pour éviter un seul chunk trop long.
    """
    import re
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    buffer = ""
    for sent in sentences:
        if len(buffer) + len(sent) <= CHUNK_MAX_LENGTH:
            buffer += " " + sent if buffer else sent
        else:
            chunks.append(buffer)
            buffer = sent
    if buffer:
        chunks.append(buffer)
    return chunks

def deduplicate_docs(docs):
    """
    Supprime les chunks très similaires (ratio > DEDUP_THRESHOLD).
    """
    unique = []
    for d in docs:
        if all(SequenceMatcher(None, d['content'], u['content']).ratio() < DEDUP_THRESHOLD for u in unique):
            unique.append(d)
    return unique

def enrich_chunks(chunks, source, theme, country):
    """
    Ajoute titres, metadata et compteur global pour chaque chunk.
    """
    global global_chunk_counter
    documents = []
    for i, chunk in enumerate(chunks):
        summary = chunk[:200]
        title = f"Chunk #{global_chunk_counter} ({source} – partie {i+1})"
        documents.append({
            "title": title,
            "content": chunk,
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

def clean_knowledge_base():
    """
    Supprime tous les documents existants.
    """
    with transaction.atomic():
        deleted_count, _ = KnowledgeDocument.objects.all().delete()
        print(f"🧹 Base nettoyée : {deleted_count} documents supprimés.")

def save_to_local_db(documents):
    """
    Sauvegarde les chunks dans la base, évite les doublons exacts.
    """
    for doc in documents:
        if not KnowledgeDocument.objects.filter(title=doc["title"], region=doc["metadata"]["country"]).exists():
            KnowledgeDocument.objects.create(
                title=doc["title"],
                content=doc["content"],
                metadata=doc["metadata"],
                region=doc["metadata"]["country"],
                theme=doc["theme"],
                summary=doc["summary"]
            )

def pdf_to_rag_pro(pdf_path, theme=DEFAULT_THEME, country=None):
    """
    Transforme un PDF en chunks RAG et sauvegarde.
    """
    source = Path(pdf_path).stem
    country = country if country else "Inconnu"
    text = extract_clean_text_from_pdf(pdf_path)
    if not text:
        print(f"⚠️ Aucun texte extrait pour {pdf_path}")
        return 0

    chunks = split_text_smart(text)
    print(f"ℹ️ {len(chunks)} chunks générés pour {source} ({country})")

    docs = enrich_chunks(chunks, source, theme, country)
    docs = deduplicate_docs(docs)
    save_to_local_db(docs)
    print(f"✅ {len(docs)} documents indexés depuis {pdf_path} ({country})")
    return len(docs)

def process_all_pdfs(root_folder=PDF_ROOT_FOLDER):
    """
    Parcourt tous les dossiers région/pays et indexe les PDFs.
    Retourne un rapport final.
    """
    if clean_base:
        clean_knowledge_base()

    root = Path(root_folder)
    total_pdfs = 0
    total_chunks = 0
    errors = []

    for country_folder in root.iterdir():
        if country_folder.is_dir():
            country_name = country_folder.name
            pdf_files = list(country_folder.glob("*.pdf"))
            for pdf_path in tqdm(pdf_files, desc=f"Indexation PDFs {country_name}"):
                total_pdfs += 1
                try:
                    chunks_created = pdf_to_rag_pro(str(pdf_path), country=country_name)
                    total_chunks += chunks_created
                except Exception as e:
                    print(f"❌ Erreur traitement {pdf_path}: {e}")
                    errors.append(str(pdf_path))

    print("\n🎯 Rapport final :")
    print(f"📄 PDFs traités : {total_pdfs}")
    print(f"📝 Chunks créés : {total_chunks}")
    print(f"⚠️ PDFs en erreur : {len(errors)}")
    if errors:
        for e in errors:
            print(f"   - {e}")

# ----------------------------
# LANCEMENT
# ----------------------------
if __name__ == "__main__":
    process_all_pdfs()