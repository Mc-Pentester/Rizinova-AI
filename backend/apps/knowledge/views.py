from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


# Pour KnowledgeList et Conseils Rapides, on n'a pas besoin de cache pour l'instant
# Mais tu peux l'ajouter si tu veux

# 🔌 API Knowledge List
class KnowledgeListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Exemple : renvoyer la liste des connaissances agricoles
        data = [
            {"title": "Fertilisation", "content": "Conseils sur l'engrais et la fertilisation"},
            {"title": "Maladies", "content": "Conseils sur la prévention des maladies du riz"},
            {"title": "Irrigation", "content": "Conseils pour l'irrigation du riz"},
            {"title": "Récolte", "content": "Conseils pour la récolte"},
            {"title": "Stockage", "content": "Conseils pour le stockage"}
        ]
        return Response(data)


# 🔌 API Conseils Rapides
class ConseilsRapidesAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Exemple : retourner quelques conseils rapides
        tips = [
            "Arrosez le riz tôt le matin",
            "Fertilisez après la levée",
            "Surveillez régulièrement les maladies",
            "Récoltez au bon moment pour éviter les pertes"
        ]
        return Response({"tips": tips})


# 🔌 API Knowledge List
class KnowledgeListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Exemple : retourner la liste des connaissances
        data = [
            {"title": "Fertilisation", "content": "Conseils sur l'engrais et la fertilisation"},
            {"title": "Maladies", "content": "Conseils sur la prévention des maladies du riz"},
            {"title": "Irrigation", "content": "Conseils pour l'irrigation du riz"},
            {"title": "Récolte", "content": "Conseils pour la récolte"},
            {"title": "Stockage", "content": "Conseils pour le stockage"}
        ]
        return Response(data)


# 🔌 API Conseils Rapides
class ConseilsRapidesAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        # Exemple : retourner quelques conseils rapides
        tips = [
            "Arrosez le riz tôt le matin",
            "Fertilisez après la levée",
            "Surveillez régulièrement les maladies",
            "Récoltez au bon moment pour éviter les pertes"
        ]
        return Response({"tips": tips})
