# app/agents/recommenderAgent.py
from openai import OpenAI
from app.core.vector_store import VectorStore
from app.core.config import settings

class RecommenderAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.vstore = VectorStore()

    def recommend(self, soil_data: str, analysis: str, language: str = "fr"):
        """Generates recommendations in the requested language."""
        system_prompt = (
            "Tu es un conseiller agricole expert en sciences du sol. Tu connais particulièrement bien les cultures et les sols africains. "
            "Génère des recommandations EN FRANÇAIS: (1) Corrections du sol (amendements, doses), (2) Cultures recommandées (exigences, fertilisation, saison)."
        )
        
        docs, _ = self.vstore.query(soil_data, n=3)
        context = "\n".join(docs[0]) if docs else "Aucun document disponible."
        
        user_prompt = f"""
CONTEXTE:
- Paramètres du sol: {soil_data}
- Interprétation: {analysis}
- Base de connaissances: {context}

INSTRUCTIONS:
Produis des recommandations claires et actionnables en suivant EXACTEMENT cette structure Markdown:

### 1. Corrections et Amendements du Sol
- Liste les actions correctives nécessaires. Pour chaque action, précise:
  - **Type d'amendement**: (ex: Compost, Chaux, Urée, NPK 15-15-15).
  - **Dose recommandée**: (ex: 5 t/ha, 150 kg/ha).
  - **Moment de l'application**: (ex: Avant le labour, au semis).
  - **Justification**: (ex: Pour corriger le pH acide, Pour augmenter le taux de matière organique).

### 2. Cultures Recommandées
- Propose 2 à 3 cultures adaptées au sol et au contexte. Pour chaque culture, fournis une fiche concise:
  - **Nom de la culture**: (ex: Maïs).
  - **Justification du choix**: (ex: Tolérant au pH légèrement acide, besoin en potassium modéré).
  - **Recommandations de fertilisation spécifiques**: (ex: NPK: 120-60-60 kg/ha, apport de 3 t/ha de compost).
  - **Conseils pratiques**: (ex: Semis en début de saison des pluies, espacement de 75cm x 25cm).
"""
        
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()