import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger les variables d'environnement
load_dotenv()

# Vérification rapide
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY non défini dans .env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(text: str):
    """Retourne l'embedding OpenAI pour un texte donné"""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding
