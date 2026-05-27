# apps/knowledge/scripts/import_rag_base_realistic.py

import os
import django
import random

# ────────────────
# ⚙️ Initialisation Django
# ────────────────
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
django.setup()

from apps.knowledge.models import KnowledgeDocument

# ────────────────
# ⚙️ Fonctions utilitaires
# ────────────────
def import_documents(doc_list):
    imported = 0
    skipped = 0

    for doc in doc_list:
        title = doc["title"].strip()
        content = doc["content"].strip()

        if not title or not content:
            skipped += 1
            continue

        if KnowledgeDocument.objects.filter(title=title).exists():
            skipped += 1
            continue

        KnowledgeDocument.objects.create(title=title, content=content)
        imported += 1

    print(f"✅ Import terminé : {imported} documents importés, {skipped} ignorés (doublons ou vides)")

# ────────────────
# ⚙️ Génération du contenu réaliste
# ────────────────
topics = [
    "Stockage du riz",
    "Techniques de semis et repiquage",
    "Gestion des mauvaises herbes",
    "Irrigation",
    "Fertilisation",
    "Protection des cultures",
    "Récolte et post-récolte",
    "Analyse économique",
    "Qualité du grain",
    "Transformation du riz"
]

practices = [
    "adaptez les techniques culturales aux conditions locales du sol et du climat",
    "planifiez l'irrigation selon les besoins en eau du cycle du riz",
    "utilisez des engrais de manière raisonnée pour éviter la sur-fertilisation",
    "surveillez les mauvaises herbes et éliminez-les régulièrement",
    "récoltez au moment optimal pour maximiser la qualité du grain",
    "stockez le riz dans un lieu sec et ventilé pour réduire les pertes",
    "suivez un protocole de transformation pour garantir la qualité du produit final",
    "intégrez des pratiques agricoles durables pour maintenir la fertilité du sol"
]

warnings = [
    "Une mauvaise application peut entraîner des pertes importantes.",
    "Évitez de négliger cette étape pour ne pas diminuer le rendement.",
    "Une gestion inadéquate peut réduire la qualité du grain.",
    "Une planification insuffisante peut augmenter les coûts de production."
]

# ────────────────
# ⚙️ Création des 6 batches de 50 documents
# ────────────────
batches = []
doc_counter = 1

for batch_num in range(6):
    batch = []
    for i in range(50):
        topic = topics[(doc_counter - 1) % len(topics)]
        practice = random.choice(practices)
        warning = random.choice(warnings)

        content = (
            f"{topic} est une étape essentielle de la riziculture. "
            f"Pour réussir, {practice}. {warning} "
            f"Ce document est le guide pratique numéro {doc_counter}, conçu pour fournir des conseils pratiques aux cultivateurs."
        )

        batch.append({
            "title": f"{topic} — Guide pratique #{doc_counter}",
            "content": content
        })

        doc_counter += 1
    batches.append(batch)

# ────────────────
# ⚙️ Import batch par batch
# ────────────────
for idx, batch in enumerate(batches):
    print(f"\n🚀 Import batch {idx+1}/6")
    import_documents(batch)

print("\n🎯 Tous les 300 documents réalistes ont été importés !")
