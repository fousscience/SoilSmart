# app/agents/extractor_agent.py
from app.agents.baseAgent import BaseAgent

class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ExtractorAgent",
            role="Tu es un assistant chargé d'extraire les paramètres d'une analyse de sol. Tu réponds TOUJOURS avec du JSON valide."
        )

    def extract_parameters(self, text: str) -> dict:
        """Retourne un dictionnaire des paramètres clés"""
        import json
        import re
        
        # Use full text - no truncation to capture all parameters
        text_sample = text
        
        prompt = f"""
        Tu dois extraire les paramètres d'analyse de sol du texte ci-dessous.
        Le texte peut être structuré (tableau) ou non structuré (paragraphes).
        
        TEXTE:
        {text_sample}
        
        INSTRUCTIONS:
        1. Cherche TOUS les paramètres de sol avec leurs valeurs numériques:
           - pH, matière organique (MO), azote (N), phosphore (P), potassium (K)
           - calcium (Ca), magnésium (Mg), sodium (Na), CEC, conductivité (CE)
           - texture (argile, limon, sable), carbone (C), C/N, etc.
        
        2. Pour chaque paramètre trouvé:
           - Si UNE SEULE valeur: {{"valeur": "5.2", "unite": "unité"}}
           - Si PLUSIEURS valeurs: {{"valeur": "4.2, 5.1, 6.3", "unite": "unité"}}
           - Si PLAGE (min-max): {{"valeur": "4.2 - 6.3", "unite": "unité"}}
           - Toujours inclure l'unité si disponible
        
        3. Accepte TOUTES les formes:
           - "pH = 6.5" ou "pH: 6.5" ou "le pH est de 6.5"
           - "MO 2.3%" ou "matière organique: 2.3 %"
           - "P: 12, 15, 18 ppm" (plusieurs échantillons)
        
        4. Si tu trouves au moins UN paramètre, retourne-le en JSON
        5. Si AUCUN paramètre n'est trouvé, retourne: {{"texte_brut": "Désolé, je n'ai pas trouvé de paramètres dans ce document"}}
        
        EXEMPLES DE RÉPONSE:
        {{
          "pH": {{"valeur": "5.3 - 7.7", "unite": ""}},
          "matiere_organique": {{"valeur": "0.28, 1.53", "unite": "%"}},
          "phosphore": {{"valeur": "12.5", "unite": "ppm"}},
          "potassium": {{"valeur": "0.4 - 7.0", "unite": "meq/100g"}}
        }}
        
        Réponds UNIQUEMENT avec du JSON valide, rien d'autre.
        """
        try:
            raw = self.run(prompt)
            print(f"\n=== RÉPONSE BRUTE EXTRACTOR ===")
            print(raw)
            print("\n=== FIN RÉPONSE ===")
            
            # Try to extract JSON from markdown code blocks if present
            json_match = re.search(r'```(?:json)?\s*({.*?})\s*```', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(1)
            
            # Clean up common issues
            raw = raw.strip()
            
            return json.loads(raw)
        except json.JSONDecodeError as e:
            print(f"\n=== ERREUR JSON ===")
            print(f"Erreur: {e}")
            print(f"Texte reçu: {raw[:200]}")
            return {"error": "Impossible d'extraire correctement les paramètres.", "raw_response": raw[:200]}
        except Exception as e:
            print(f"\n=== ERREUR GENERALE ===")
            print(f"Erreur: {e}")
            return {"error": f"Erreur lors de l'extraction: {str(e)}"}
