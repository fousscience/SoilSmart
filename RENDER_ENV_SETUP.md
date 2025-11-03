# Configuration des Variables d'Environnement sur Render

## 🎯 Résumé : Variables Redis (Upstash)

**Réponse courte :** ❌ **NON**, vous n'avez **PAS besoin** d'ajouter les variables Redis sur le service Streamlit.

Seul le **service API** (FastAPI) a besoin de Redis.

---

## 📋 Configuration par Service

### Service API (FastAPI) - ✅ **OBLIGATOIRE**

Ce service utilise Redis pour le cache des rapports.

**Variables d'environnement requises :**

```bash
# Variables obligatoires
OPENAI_API_KEY=votre_clé_openai
API_URL=https://votre-api.render.com

# Variables Redis (Optionnel mais recommandé)
REDIS_HOST=redis://default:VOTRE_PASSWORD@VOTRE_HOST.upstash.io:6379
REDIS_TTL=3600

# Optimisation
UVICORN_WORKERS=2
```

**Où ajouter :** 
- Render Dashboard → **Votre service API** → **Environment** → **Add Environment Variable**

---

### Service Streamlit (Frontend) - ❌ **PAS BESOIN**

Ce service ne gère **PAS** Redis directement. Il fait uniquement des appels HTTP à l'API.

**Variables d'environnement requises :**

```bash
# Variable obligatoire (pointer vers votre API)
API_URL=https://votre-api.render.com
```

**Où ajouter :** 
- Render Dashboard → **Votre service Streamlit** → **Environment** → **Add Environment Variable**

---

## 🔍 Pourquoi cette architecture ?

### Architecture Actuelle :
```
┌─────────────────┐
│  Streamlit      │  (Frontend)
│  (Frontend)     │
│                 │
│  Fait des appels│
│  HTTP à l'API  │
└────────┬────────┘
         │ HTTP
         │
         ▼
┌─────────────────┐
│  FastAPI        │  (Backend)
│  (API)          │
│                 │
│  ✅ Utilise     │
│  Redis Cache    │
│                 │
│  ✅ Traite les  │
│  fichiers PDF   │
└─────────────────┘
```

**Le service Streamlit :**
- ✅ Affiche l'interface utilisateur
- ✅ Fait des requêtes HTTP à l'API
- ❌ Ne gère PAS Redis
- ❌ Ne traite PAS les fichiers PDF

**Le service API :**
- ✅ Reçoit les fichiers PDF
- ✅ Traite les analyses
- ✅ **Utilise Redis pour le cache** ← Ici seulement
- ✅ Retourne les résultats au frontend

---

## ✅ Checklist de Configuration

### Service API (FastAPI)
- [ ] `OPENAI_API_KEY` configurée
- [ ] `API_URL` configurée (URL de votre API)
- [ ] `REDIS_HOST` configurée (URL Upstash)
- [ ] `REDIS_TTL` configurée (optionnel, défaut: 3600)
- [ ] `UVICORN_WORKERS` configurée (optionnel, défaut: 2)

### Service Streamlit (Frontend)
- [ ] `API_URL` configurée (URL de votre API, pas du Streamlit)

---

## 🧪 Vérification après Configuration

### Vérifier que Redis fonctionne sur l'API :

1. **Consulter les logs du service API** :
   ```
   ✅ Redis cache connected
   ```

2. **Tester l'endpoint `/health`** :
   ```bash
   GET https://votre-api.render.com/health
   ```
   Réponse attendue :
   ```json
   {
     "status": "ok",
     "cache": "redis"
   }
   ```

### Si vous voyez `"cache": "memory"` :
- Vérifiez que `REDIS_HOST` est bien configurée sur le **service API uniquement**
- Vérifiez que l'URL Redis est correcte (pas d'espaces)
- Vérifiez les logs pour les erreurs de connexion

---

## 🆘 Erreurs Communes

### Erreur : "Redis not available"
- ❌ Vous avez peut-être ajouté Redis sur le mauvais service (Streamlit)
- ✅ Solution : Vérifiez que Redis est configuré sur le **service API** uniquement

### Erreur : "API_URL not found" (dans Streamlit)
- ✅ Solution : Ajoutez `API_URL` sur le **service Streamlit**, pointant vers votre API

---

## 📝 Résumé Rapide

| Variable | Service API | Service Streamlit |
|----------|-------------|-------------------|
| `REDIS_HOST` | ✅ **OUI** | ❌ **NON** |
| `REDIS_TTL` | ✅ **OUI** | ❌ **NON** |
| `OPENAI_API_KEY` | ✅ **OUI** | ❌ **NON** |
| `API_URL` | ✅ **OUI** | ✅ **OUI** (vers API) |
| `UVICORN_WORKERS` | ✅ **OUI** | ❌ **NON** |

---

**Note importante :** Le service Streamlit n'a **aucun accès direct** à Redis. Tous les appels cache se font via l'API. C'est l'API qui bénéficie du cache Redis, et le frontend Streamlit bénéficie indirectement de la rapidité de l'API.

