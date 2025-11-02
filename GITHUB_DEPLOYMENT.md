# Guide de Déploiement sur GitHub - SoilSmart

## 📋 Prérequis

1. **Compte GitHub** créé
2. **Git installé** sur votre machine
3. **Accès SSH** ou **HTTPS** configuré pour GitHub

## 🚀 Étapes de Déploiement

### Étape 1 : Vérifier l'état du dépôt Git

Ouvrez un terminal dans le dossier du projet et vérifiez l'état :

```bash
git status
```

### Étape 2 : Vérifier la configuration Git (si nécessaire)

```bash
# Vérifier votre nom et email
git config user.name
git config user.email

# Configurer si nécessaire (remplacez par vos informations)
git config user.name "Votre Nom"
git config user.email "votre.email@example.com"
```

### Étape 3 : Créer un fichier .gitignore (si absent)

Vérifiez qu'un fichier `.gitignore` existe pour exclure les fichiers sensibles :

```bash
# Si .gitignore n'existe pas, créez-le avec :
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
.env.local

# Application data
app/data/
*.db
*.sqlite

# Logs
*.log

# OS
.DS_Store
Thumbs.db

# Documentation build
*.pdf
docs/_build/

# Temporary files
*.tmp
*.temp
EOF
```

### Étape 4 : Ajouter tous les fichiers modifiés

```bash
# Ajouter tous les fichiers (nouveaux et modifiés)
git add .

# OU ajouter des fichiers spécifiques :
# git add requirements.txt Dockerfile app/ frontend/
```

### Étape 5 : Vérifier les fichiers à commiter

```bash
# Vérifier ce qui va être commité
git status

# Voir les différences
git diff --staged
```

### Étape 6 : Créer un commit

```bash
# Créer un commit avec un message descriptif
git commit -m "feat: Add Redis cache, optimizations, and deployment configurations

- Add Redis caching system with Upstash support
- Implement singleton pattern for OpenAI clients and OrchestratorAgent
- Add Uvicorn workers configuration
- Optimize Dockerfile with layer caching
- Add PDF generation with xhtml2pdf
- Update documentation (Redis setup, optimizations)
- Fix Dockerfile build tools cleanup"
```

**Messages de commit recommandés** :
- `feat:` pour nouvelles fonctionnalités
- `fix:` pour corrections de bugs
- `docs:` pour documentation
- `refactor:` pour refactorisation
- `perf:` pour optimisations

### Étape 7 : Vérifier le dépôt distant

```bash
# Vérifier si un dépôt distant est configuré
git remote -v
```

### Étape 8 : Ajouter/Créer le dépôt GitHub

#### Option A : Si le dépôt GitHub existe déjà

```bash
# Si vous avez déjà créé le dépôt sur GitHub, ajoutez-le :
git remote add origin https://github.com/VOTRE_USERNAME/soilsmart.git

# OU avec SSH :
git remote add origin git@github.com:VOTRE_USERNAME/soilsmart.git
```

#### Option B : Créer un nouveau dépôt sur GitHub

1. **Aller sur GitHub.com**
2. **Cliquer sur le "+"** en haut à droite → **"New repository"**
3. **Configurer le dépôt** :
   - **Name** : `soilsmart`
   - **Description** : "SoilSmart - Analyse intelligente de rapports de sol avec IA"
   - **Visibilité** : Public ou Private (selon votre choix)
   - **NE PAS** cocher "Add a README file" (si vous avez déjà du code local)
   - **NE PAS** ajouter .gitignore (vous en avez déjà un)
4. **Cliquer sur "Create repository"**
5. **Copier l'URL** du dépôt (HTTPS ou SSH)

```bash
# Ajouter le dépôt distant
git remote add origin https://github.com/VOTRE_USERNAME/soilsmart.git
```

### Étape 9 : Pousser vers GitHub

```bash
# Si c'est la première fois (branche principale peut être main ou master)
git branch -M main  # S'assurer que la branche s'appelle "main"

# Pousser vers GitHub
git push -u origin main
```

**Si vous rencontrez une erreur d'authentification :**

#### Pour HTTPS :
1. Utiliser un **Personal Access Token** au lieu du mot de passe
2. Générer un token : GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
3. Utiliser le token comme mot de passe

#### Pour SSH :
1. Générer une clé SSH si nécessaire :
   ```bash
   ssh-keygen -t ed25519 -C "votre.email@example.com"
   ```
2. Ajouter la clé à GitHub : GitHub → Settings → SSH and GPG keys → New SSH key

### Étape 10 : Vérifier sur GitHub

1. **Aller sur votre dépôt GitHub** : `https://github.com/VOTRE_USERNAME/soilsmart`
2. **Vérifier que tous les fichiers sont présents**
3. **Vérifier que le README.md est à jour** (optionnel)

## 🔄 Commandes Git Utiles

### Voir l'historique des commits
```bash
git log --oneline
```

### Annuler le dernier commit (garder les modifications)
```bash
git reset --soft HEAD~1
```

### Mettre à jour depuis GitHub
```bash
git pull origin main
```

### Créer une nouvelle branche
```bash
git checkout -b feature/nouvelle-fonctionnalite
```

### Voir les différences
```bash
git diff
```

## ⚠️ Fichiers à NE PAS commiter

Assurez-vous que votre `.gitignore` exclut :
- **`.env`** : Variables d'environnement (OPENAI_API_KEY, etc.)
- **`app/data/`** : Données de l'application
- **`__pycache__/`** : Fichiers Python compilés
- **`*.log`** : Fichiers de log
- **Fichiers sensibles** : Clés API, mots de passe, etc.

## ✅ Checklist avant de pousser

- [ ] `.gitignore` est à jour
- [ ] Fichiers sensibles (`.env`) sont exclus
- [ ] Tous les fichiers nécessaires sont ajoutés
- [ ] Message de commit est descriptif
- [ ] Dépendances dans `requirements.txt` sont à jour
- [ ] `Dockerfile` est correct
- [ ] Documentation est à jour
- [ ] Testé localement (si possible)

## 🚀 Après le Push sur GitHub

### Pour déployer sur Render :

1. **Aller sur Render Dashboard**
2. **Service** → **Settings** → **Build Command**
   - Laisser vide (Render détecte automatiquement Docker)
3. **Service** → **Environment**
   - Vérifier que toutes les variables d'environnement sont configurées
4. **Manuel Deploy** (si nécessaire)
   - Render redéploie automatiquement après un push, ou déclencher manuellement

### Vérifier le déploiement :

1. **Consulter les logs Render**
2. **Tester l'endpoint `/health`**
3. **Vérifier que Redis se connecte** : `✅ Redis cache connected`

## 🆘 Dépannage

### Erreur : "repository not found"
- Vérifier l'URL du dépôt distant
- Vérifier les permissions d'accès au dépôt

### Erreur : "authentication failed"
- Utiliser un Personal Access Token (HTTPS)
- Ou configurer SSH correctement

### Erreur : "failed to push some refs"
- Faire un `git pull origin main` avant de pousser
- Résoudre les conflits si nécessaire

## 📝 Commandes Rapides (Résumé)

```bash
# 1. Vérifier l'état
git status

# 2. Ajouter les fichiers
git add .

# 3. Créer un commit
git commit -m "feat: Add Redis cache and optimizations"

# 4. Pousser vers GitHub
git push -u origin main
```

---

**Note** : Assurez-vous de ne jamais commiter de fichiers `.env` contenant des clés API ou des mots de passe. Utilisez toujours les variables d'environnement sur Render.

