# apps/knowledge/models.py
from django.db import models
from django.utils import timezone
import hashlib

from django.db import models
import json
import numpy as np

class KnowledgeDocument(models.Model):
    title = models.CharField(max_length=500)
    content = models.TextField()
    region = models.CharField(max_length=200, blank=True, null=True)
    theme = models.CharField(max_length=200, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    embedding_json = models.TextField(blank=True, null=True)  # Stockage embedding en JSON

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ===============================
    # UTILITAIRES EMBEDDING
    # ===============================
    def set_embedding(self, vec: np.ndarray):
        """Convertit un np.array en JSON et stocke"""
        self.embedding_json = json.dumps(vec.tolist())

    def get_embedding(self) -> np.ndarray:
        """Récupère l'embedding stocké en JSON comme np.array"""
        if not self.embedding_json:
            return None
        return np.array(json.loads(self.embedding_json), dtype=np.float32)
        
    def __str__(self):
        return f"{self.title} ({self.region or 'Région non précisée'})"


class QuestionHistory(models.Model):
    question = models.TextField()
    theme = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.theme


class CachedAnswer(models.Model):
    question_hash = models.CharField(
        max_length=64,
        unique=True,
        db_index=True
    )
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return (self.question or "")[:50]

    @staticmethod
    def hash_question(question: str) -> str:
        normalized = question.strip().lower()
        return hashlib.sha256(
            normalized.encode("utf-8")
        ).hexdigest()


# apps/knowledge/models.py

class ConversationMessage(models.Model):
    user_id = models.CharField(max_length=100)
    role = models.CharField(max_length=20)  # "user" / "assistant"
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)