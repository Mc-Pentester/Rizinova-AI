from rest_framework import serializers
from .models import KnowledgeDocument

class KnowledgeDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KnowledgeDocument
        fields = ['id', 'title', 'content', 'region', 'metadata']
