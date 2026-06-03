import os
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
import logging

logger = logging.getLogger('api')


# ==================== SERIALIZERS ====================

class KnowledgeSearchSerializer(serializers.Serializer):
    """Serializer pour la recherche de connaissances"""
    query = serializers.CharField(max_length=500)
    category = serializers.CharField(max_length=100, required=False)
    region = serializers.CharField(max_length=100, required=False)


class RAGResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse RAG"""
    query = serializers.CharField()
    results = serializers.ListField()
    answer = serializers.CharField()
    confidence = serializers.FloatField()


class HealthCheckSerializer(serializers.Serializer):
    """Serializer pour le health check"""
    status = serializers.CharField()
    database = serializers.CharField()
    api = serializers.CharField()
    redis = serializers.CharField()


# ==================== API VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint
    
    Returns:
        200: Status de santé du système
    """
    from django.db import connection
    
    health_status = {
        'status': 'healthy',
        'database': 'unknown',
        'api': 'ok',
        'redis': 'unknown',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }
    
    # Vérifier la base de données
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['database'] = 'ok'
    except Exception as e:
        health_status['database'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
        logger.warning(f"Database health check failed: {e}")
    
    logger.info("Health check performed", extra={'status': health_status['status']})
    return Response(health_status, status=HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_knowledge(request):
    """
    Recherche de connaissances RAG
    
    Parameters:
        query: Texte de recherche
        category: Catégorie (optionnel)
        region: Région (optionnel)
    
    Returns:
        200: Résultats de recherche avec réponse IA
        400: Erreur de validation
    """
    serializer = KnowledgeSearchSerializer(data=request.data)
    
    if not serializer.is_valid():
        logger.warning(f"Invalid search request from {request.user}", extra=serializer.errors)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    query = serializer.validated_data.get('query')
    category = serializer.validated_data.get('category')
    region = serializer.validated_data.get('region')
    
    logger.info(
        f"Knowledge search performed",
        extra={
            'user': request.user.username,
            'query': query,
            'category': category,
            'region': region
        }
    )
    
    # Implémenter la logique RAG ici
    response_data = {
        'query': query,
        'results': [],
        'answer': 'Résultats de la recherche',
        'confidence': 0.85
    }
    
    return Response(response_data, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Récupérer le profil utilisateur actuel
    
    Returns:
        200: Informations de l'utilisateur
    """
    user_data = {
        'id': request.user.id,
        'username': request.user.username,
        'email': request.user.email,
        'is_active': request.user.is_active,
        'date_joined': request.user.date_joined.isoformat(),
    }
    
    logger.info(f"User profile accessed by {request.user.username}")
    return Response(user_data, status=HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_quota_status(request):
    """
    Récupérer le statut du quota de l'utilisateur
    
    Returns:
        200: Statut de quota
    """
    # À implémenter avec un système de quota
    quota_data = {
        'requests_today': 0,
        'requests_limit': 1000,
        'remaining': 1000,
        'reset_at': __import__('datetime').datetime.now().isoformat()
    }
    
    logger.info(f"Quota status checked for {request.user.username}")
    return Response(quota_data, status=HTTP_200_OK)
