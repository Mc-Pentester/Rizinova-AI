from apps.knowledge.models import KnowledgeDocument

def list_documents(limit=10, region=None):
    qs = KnowledgeDocument.objects.all()
    if region:
        qs = qs.filter(region=region)
    docs = []
    for d in qs[:limit]:
        docs.append({
            "id": d.id,
            "title": d.title,
            "region": d.region,
            "metadata": d.metadata,
            "content_preview": d.content[:200]
        })
    return docs

def print_documents(docs):
    for d in docs:
        print(f"ID: {d['id']} | Titre: {d['title']} | Region: {d['region']} | Metadata: {d['metadata']}")
        print(f"Contenu (aperçu) : {d['content_preview']}...\n")

def read_document(doc_id):
    try:
        d = KnowledgeDocument.objects.get(id=doc_id)
        return {
            "id": d.id,
            "title": d.title,
            "region": d.region,
            "metadata": d.metadata,
            "content": d.content
        }
    except KnowledgeDocument.DoesNotExist:
        return None

def search_documents(keyword, limit=10):
    qs = KnowledgeDocument.objects.filter(content__icontains=keyword) | \
         KnowledgeDocument.objects.filter(title__icontains=keyword)
    docs = []
    for d in qs[:limit]:
        docs.append({
            "id": d.id,
            "title": d.title,
            "region": d.region,
            "metadata": d.metadata,
            "content_preview": d.content[:200]
        })
    return docs

def start_console():
    print("=== Console RAG Interactive ===")
    while True:
        print("\nOptions :")
        print("1. Lister les documents")
        print("2. Lire un document par ID")
        print("3. Rechercher par mot-clé")
        print("4. Quitter")

        choice = input("Choix (1-4) : ").strip()

        if choice == "1":
            region = input("Filtrer par region (laisser vide pour tous) : ").strip()
            region = region if region else None
            docs = list_documents(limit=20, region=region)
            if docs:
                print_documents(docs)
            else:
                print("Aucun document trouvé.")

        elif choice == "2":
            doc_id = input("ID du document : ").strip()
            if not doc_id.isdigit():
                print("ID invalide.")
                continue
            doc = read_document(int(doc_id))
            if doc:
                print(f"\nTitre: {doc['title']}")
                print(f"Region: {doc['region']}")
                print(f"Metadata: {doc['metadata']}")
                print(f"Contenu complet:\n{doc['content']}\n")
            else:
                print("Document introuvable.")

        elif choice == "3":
            keyword = input("Mot-clé à rechercher : ").strip()
            docs = search_documents(keyword, limit=20)
            if docs:
                print_documents(docs)
            else:
                print("Aucun document trouvé pour ce mot-clé.")

        elif choice == "4":
            print("Fermeture de la console.")
            break
        else:
            print("Choix invalide. Réessayez.")

if __name__ == "__main__":
    start_console()
