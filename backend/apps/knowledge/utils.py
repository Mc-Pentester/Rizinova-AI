import openai
from .models import KnowledgeEmbedding

openai.api_key = "YOUR_API_KEY"

def embed_text(text):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
