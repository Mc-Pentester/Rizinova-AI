import random
from apps.knowledge.models import KnowledgeDocument

# 🔹 Symptômes possibles et actions recommandées
symptoms = [
    {"symptom": "feuilles jaunes", "stage": "montaison", "causes": ["carence en azote", "stress hydrique"], "actions": ["apport fractionné d'azote", "vérifier l'irrigation"]},
    {"symptom": "feuilles sèches", "stage": "repiquage", "causes": ["manque d'eau", "brûlure de l'engrais"], "actions": ["arrosage régulier", "réduire engrais chimique"]},
    {"symptom": "taches brunes sur les feuilles", "stage": "toutes phases", "causes": ["maladie fongique"], "actions": ["traitement fongicide", "éviter humidité stagnante"]},
    {"symptom": "grains chétifs", "stage": "maturation", "causes": ["carence en potassium", "stress hydrique"], "actions": ["apport de K", "gestion de l'irrigation"]},
    {"symptom": "pousse faible", "stage": "semis", "causes": ["semences de mauvaise qualité", "sol pauvre"], "actions": ["sélection semences", "fertilisation de sol"]},
]

sources = [f"Guide pratique #{i}" for i in range(1, 301)]

# 🔹 Paramètres de génération
TOTAL_DOCS = 300
BATCH_SIZE = 50

def generate_document(i):
    s = random.choice(symptoms)
    content = (
        f"{s['symptom'].capitalize()} au stade {s['stage']}. "
        f"Causes possibles : {', '.join(s['causes'])}. "
        f"Actions recommandées : {', '.join(s['actions'])}."
    )
    return {
        "title": f"{s['symptom'].capitalize()} — Guide pratique #{i+1}",
        "content": content,
        "source": sources[i],
    }

# 🔹 Nettoyer la base avant import
deleted_count, _ = KnowledgeDocument.objects.all().delete()
print(f"✅ Base nettoyée : {deleted_count} documents supprimés.")

# 🔹 Import par batch
for batch_start in range(0, TOTAL_DOCS, BATCH_SIZE):
    batch = [generate_document(i) for i in range(batch_start, min(batch_start + BATCH_SIZE, TOTAL_DOCS))]
    
    # Vérification doublons title
    unique_docs = []
    seen_titles = set()
    for d in batch:
        if d["title"] not in seen_titles:
            seen_titles.add(d["title"])
            unique_docs.append(d)
    
    # Création en base
    KnowledgeDocument.objects.bulk_create([
        KnowledgeDocument(title=d["title"], content=d["content"], source=d["source"]) for d in unique_docs
    ])
    print(f"✅ Batch {batch_start//BATCH_SIZE + 1} importé ({len(unique_docs)} documents uniques)")

print(f"🎯 Import terminé : {KnowledgeDocument.objects.count()} documents dans la base.")
