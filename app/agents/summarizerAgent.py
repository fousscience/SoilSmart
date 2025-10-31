# app/agents/summarizerAgent.py
from openai import OpenAI
from app.core.config import settings

class SummarizerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def summarize(self, text_to_summarize: str, target_language: str) -> str:
        """Summarizes the given text into the target language (Wolof or Bambara) using OpenAI."""
        
        system_prompts = {
            "wo": (
                "Tu es un ingénieur Agronome expérimenté et expert en sciences du sol qui résume des rapports pour des agriculteurs sénégalais (niveau d'éducation bas ou analphabète). "
                "Résume le texte suivant en WOLOF de manière simple et directe. "
                "Concentre-toi sur les points clés: (1) l'état du sol, (2) les problèmes, (3) les actions à faire. "
                "Utilise des phrases courtes et des mots comme: 'Sól si' (ce sol), 'li ci nekk' (ce qu'il y a dedans), 'li wàcc' (ce qu'il faut faire)."
            ),
            "bm": (
                "Tu es un ingénieur Agronome expérimenté et expert en sciences du sol qui résume des rapports pour des agriculteurs maliens (niveau d'éducation bas ou analphabète). "
                "Résume le texte suivant en BAMBARA de manière simple et directe. "
                "Concentre-toi sur les points clés: (1) l'état du sol, (2) les problèmes, (3) les actions à faire. "
                "Utilise des phrases courtes et des mots comme: 'Dugukolo ni' (ce sol), 'a kɔnɔna' (ce qu'il contient), 'min ka kan ka kɛ' (ce qu'il faut faire)."
            )
        }
        
        system_prompt = system_prompts.get(target_language)
        if not system_prompt:
            return f"Le langage '{target_language}' n'est pas supporté pour le résumé."

        user_prompt = f"""
TEXTE À RÉSUMER:
---
{text_to_summarize}
---

RÉSUMÉ CONCIS EN {target_language.upper()}:
        """
        
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()