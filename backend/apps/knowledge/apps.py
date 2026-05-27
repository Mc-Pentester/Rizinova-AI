# apps/knowledge/apps.py
from django.apps import AppConfig

class KnowledgeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.knowledge"

    def ready(self):
        """
        ⚠️ Chargement lazy du RAG au démarrage :
        - Initialise FAISS + BM25 pour que le moteur soit prêt
        - Pas de PDF généré ici
        """
        try:
            # import lazy pour éviter problème de cycle
            from apps.knowledge.report_service import load_index
            load_index()
            print("RAG index loaded successfully at startup.")
        except Exception as e:
            print("RAG index not loaded at startup:", e)