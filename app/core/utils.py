# app/core/utils.py
import re

def clean_text(text: str) -> str:
    """Nettoie un texte brut (supprime caractères inutiles)"""
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text
