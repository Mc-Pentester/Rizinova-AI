# apps/knowledge/scripts/clean_rag_base.py

import os
import django
import re

# ---------------------------
# ⚙️ Initialisation Django
# ---------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from apps.knowledge.models import KnowledgeDocument

# ---------------------------
# 🔹 Fonctions utilitaires
# ---------------------------

# Phrases génériques à nettoyer
GENERIC_PHRASES = [
    "dans la gestion efficiente du rendement du riz",
    "une mauvaise application de cette pratique",
    "pour réduire les pertes post-récolte",
    "une approche intégrée",
    "notamment en zone pluviale",
    "la qualité du riz destiné à la consommation ou à la transformation"
]

def remove_generic_sentences(text, phrases):
    """Supprime les phrases génériques répétitives"""
    for phrase in phrases:
        text = text.replace(phrase, "")
    text = re.sub(r"\s{2,}", " ", text)  # nettoyer les espaces multiples
    return text.strip()

def text_to_vector(text):
    """Transforme un texte en vecteur simple pour comparaison"""
    words = text.lower().split()
    vector = {}
    for w in words:
        vector[w] = vector.get(w, 0) + 1
    return vector

def cosine_similarity_dict(vec1, vec2):
    """Cosine similarity entre deux vecteurs dictionnaires"""
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([v**2 for v in vec1.values()])
    sum2 = sum([v**2 for v in vec2.values()])
    denominator = (sum1**0.5) * (sum2**0.5)
    if not denominator:
        return 0.0
    return numerator / denominator

def deduplicate_documents(docs, threshold=0.85):
    """Supprime les documents trop similaires"""
    unique_docs = []
    vectors = []

    for doc in docs:
        vec = text_to_vector(doc["content"])
        is_duplicate = False
        for v in vectors:
            if cosine_similarity_dict(vec, v) >= threshold:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_docs.append(doc)
            vectors.append(vec)
    return unique_docs

# ---------------------------
# 🔹 Nettoyage et déduplication
# ---------------------------

def clean_rag_base():
    all_docs = KnowledgeDocument.objects.all()
    print(f"🔹 Total documents dans la base : {len(all_docs)}")

    clean_docs = []
    for i, doc in enumerate(all_docs, start=1):
        print(f"Processing document {i}/{len(all_docs)} : {doc.title}")
        clean_content = remove_generic_sentences(doc.content, GENERIC_PHRASES)
        clean_docs.append({"title": doc.title, "content": clean_content})

    print("🔹 Déduplication des documents...")
    unique_docs = deduplicate_documents(clean_docs)

    print(f"🔹 Documents après nettoyage et déduplication : {len(unique_docs)}")

    # Mettre à jour la DB avec le contenu nettoyé
    for doc in unique_docs:
        db_doc = KnowledgeDocument.objects.get(title=doc["title"])
        db_doc.content = doc["content"]
        db_doc.save()

    print("✅ Base RAG nettoyée et prête à l'emploi !")

# ---------------------------
# 🔹 Lancer le script
# ---------------------------
if __name__ == "__main__":
    clean_rag_base()
