# Checklist de Déploiement - SoilSmart

## ✅ Vérifications Pré-déploiement

### 1. Requirements.txt ✅
Toutes les dépendances sont présentes et nécessaires :

- **FastAPI & Uvicorn** : `fastapi`, `uvicorn[standard]` ✓
- **Streamlit** : `streamlit` ✓
- **Base de données vectorielle** : `chromadb` ✓
- **OpenAI** : `openai` ✓
- **Configuration** : `python-dotenv` ✓
- **Validation** : `pydantic` ✓
- **OCR** : `pytesseract`, `pdf2image`, `Pillow`, `PyMuPDF` ✓
- **LangChain** : `langchain` (dépendance optionnelle de chromadb) ✓
- **HTTP** : `requests`, `python-multipart` ✓
- **PDF Generation** : `xhtml2pdf`, `markdown` ✓
- **Cache** : `redis`, `hiredis` ✓

### 2. Dockerfile ✅
- ✅ Structure optimisée avec cache des layers
- ✅ Dépendances système complètes (Cairo, Pango pour xhtml2pdf)
- ✅ Build tools installés puis supprimés pour réduire la taille
- ✅ Commandes correctes pour Uvicorn et Streamlit
- ✅ Ports exposés (8000 pour API, 8501 pour Streamlit)
- ✅ Workers Uvicorn configurés via variable d'environnement

### 3. Configuration Redis ✅
- ✅ Support des URLs Redis (format `redis://` ou `rediss://`)
- ✅ Support du format Host/Port séparé
- ✅ Fallback en cache mémoire si Redis non disponible
- ✅ Variables d'environnement configurées sur Render

## 📋 Variables d'Environnement Requises sur Render

### Obligatoires :
```bash
OPENAI_API_KEY=votre_clé_openai
API_URL=https://votre-api.render.com
```

### Optionnelles mais Recommandées :
```bash
# Redis (Upstash)
REDIS_HOST=redis://default:PASSWORD@HOST.upstash.io:6379
REDIS_TTL=3600

# Uvicorn Workers
UVICORN_WORKERS=2

# OCR (si nécessaire)
TESSERACT_CMD=/usr/bin/tesseract
OCR_LANGUAGE=fra
```

## 🚀 Étapes de Déploiement

1. **Pousser vers GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment: Redis cache + optimizations"
   git push origin main
   ```

2. **Sur Render**
   - Aller dans votre service
   - Vérifier que les variables d'environnement sont configurées
   - Déclencher un redéploiement si nécessaire

3. **Vérifier après déploiement**
   - Consulter les logs Render
   - Vérifier que vous voyez : `✅ Redis cache connected`
   - Tester l'endpoint `/health` : devrait retourner `{"status": "ok", "cache": "redis"}`

## 🔍 Points d'Attention

### Si Redis ne se connecte pas :
- Vérifier que l'URL Redis est complète et sans espaces
- Vérifier que le mot de passe est correct
- L'application fonctionnera quand même avec le cache mémoire

### Si le build Docker échoue :
- Vérifier que toutes les dépendances système sont installées
- Vérifier que les build tools sont disponibles pendant l'installation

### Si les workers Uvicorn ne démarrent pas :
- Vérifier la variable `UVICORN_WORKERS` (défaut: 2)
- Consulter les logs pour les erreurs de démarrage

## ✅ Tout est prêt !

Les fichiers `requirements.txt` et `Dockerfile` sont conformes et optimisés pour le déploiement.

