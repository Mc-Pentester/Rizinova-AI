from django.urls import path
from .views import KnowledgeListAPIView, ConseilsRapidesAPIView

urlpatterns = [
    # Liste des connaissances
    path("api/knowledge/", KnowledgeListAPIView.as_view(), name="knowledge-list"),

    # Conseils rapides
    path("api/conseils/", ConseilsRapidesAPIView.as_view(), name="conseils-rapides"),
]
