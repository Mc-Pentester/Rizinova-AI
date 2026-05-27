import openai
from backend.apps.knowledge.services.rag import retrieve_knowledge

SYSTEM_PROMPT = """
Tu es un ingénieur agronome expert en riziculture tropicale.
Utilise uniquement le contexte fourni.
Donne des conseils simples et peu coûteux.
"""

def generate_answer(question):
    context_docs = retrieve_knowledge(question)

    context = "\n\n".join(context_docs)

    prompt = f"""
Contexte agricole :
{context}

Question :
{question}
"""

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
