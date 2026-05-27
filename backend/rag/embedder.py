import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger les variables d'environnement
load_dotenv()

# Vérification rapide
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY non défini dans .env")

client = OpenAI(api_key=OPENAI_API_KEY)

def embed_text(text: str):
    """
    Retourne l'embedding OpenAI pour un texte donné
    
    Args:
        text: Le texte à embedder
        
    Returns:
        Liste de floats représentant l'embedding
        
    Raises:
        ValueError: Si le texte est vide
        Exception: Si l'API OpenAI échoue
    """
    if not text or not isinstance(text, str):
        raise ValueError("Le texte doit être une chaîne non vide")
    
    try:
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Erreur OpenAI API : {e}")
        raise
