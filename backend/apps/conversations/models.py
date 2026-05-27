from django.db import models
from django.contrib.auth.models import User

# -------------------------------
# Conversation principale
# -------------------------------
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user}"


# -------------------------------
# Messages individuels
# -------------------------------
class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name="messages"
    )
    content = models.TextField()
    is_user = models.BooleanField(default=True)  # True = message utilisateur, False = réponse IA
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = "User" if self.is_user else "RAG/IA"
        return f"{sender}: {self.content[:30]}..."
