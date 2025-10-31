# 🌱 SoilSmart

SoilSmart est une application d’intelligence artificielle pour l’analyse des sols et les recommandations agronomiques.

## 🚀 Technologies
- **Backend :** FastAPI + OpenAI Agents
- **Frontend :** Streamlit
- **Base vectorielle :** ChromaDB
- **Conteneurisation :** Docker
- **Déploiement :** Render

## ⚙️ Lancer en local

```bash
uv sync requirements.txt
uv run uvicorn app.main:app --reload
uv run streamlit run frontend/streamlit_app.py
