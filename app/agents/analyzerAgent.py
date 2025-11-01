# app/agents/analyzerAgent.py
from openai import OpenAI
from app.core.config import settings
import json

class AnalyzerAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def interpret(self, soil_data: dict, language: str = "fr") -> str:
        """Returns a clear agronomic interpretation in the requested language."""
        system_prompt = (
            "Tu es un agronome expert en sciences du sol. Tu maitrises particulièrement bien les cultures et les sols ouest africains "
            "(Sénégal, Mali, Burkina Faso, Côte d'Ivoire, Guinée). Analyse ces paramètres de sol et fournis une interprétation "
            "détaillée EN FRANÇAIS, couvrant l'état général, l'analyse par paramètre (n'ignore aucun paramètre), les points forts/faiblesses, et les priorités."
        )
        params_text = json.dumps(soil_data, indent=2, ensure_ascii=False)
        
        user_prompt = f"""
PARAMÈTRES DU SOL:
{params_text}

INSTRUCTIONS:
Fournis une interprétation agronomique détaillée en suivant EXACTEMENT cette structure Markdown:

### 1. État Général du Sol
- Résumé sur la santé globale du sol (pauvre, moyen, bon, excellent).
- Mentionne le principal facteur limitant (ex: acidité, manque de matière organique).

### 2. Analyse Détaillée par Paramètre (n'ignore aucun paramètre extrait)
- **pH**: Niveau et implication (acide, neutre, basique).
- **Matière Organique**: Niveau et son importance pour la fertilité.
- **Azote (N), Phosphore (P), Potassium (K)**: Niveaux individuels (faible, moyen, élevé) et équilibre N-P-K.
- **Capacité d'Échange Cationique (CEC)**: Niveau et ce que cela signifie pour la rétention des nutriments.
- **Autres paramètres**: Mentionne tout autre paramètre clé (ex: Texture, Conductivité).

### 3. Conclusion et Priorités
- **Points Forts**: Liste 2-3 aspects positifs du sol.
- **Points Faibles**: Liste 2-3 aspects négatifs à corriger.
- **Action Prioritaire**: Quelle est la chose la plus importante à faire en premier ?
"""
        
        response = self.client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()