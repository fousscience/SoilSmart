# Guide de Configuration Redis pour SoilSmart

## 🎯 Pourquoi utiliser Redis ?

Redis améliore significativement les performances en mettant en cache les rapports déjà analysés. Un fichier PDF identique sera servi instantanément depuis le cache au lieu de refaire toute l'analyse.

## 📋 Options pour obtenir Redis

### Option 1 : Upstash Redis (Recommandé - Gratuit)

**Avantages :**
- Plan gratuit généreux (10 000 commandes/jour)
- Gestion automatique (serverless)
- Pas de limite de temps
- Facile à configurer

**Étapes :**

1. **Créer un compte Upstash**
   - Aller sur https://upstash.com/
   - Cliquer sur "Sign Up" (créer un compte)
   - S'authentifier avec GitHub, Google ou email

2. **Créer une base de données Redis**
   - Dans le dashboard Upstash
   - Cliquer sur "Create Database"
   - Choisir "Global" (meilleure latence) ou région spécifique
   - Choisir "Redis" comme type
   - Plan : "Free" (plan gratuit)
   - Donner un nom à votre base (ex: "ch")

3. **Récupérer les informations de connexion**
   - Une fois créée, cliquer sur votre base de données
   - Dans l'onglet "Details", vous verrez :
     - **Endpoint** (host) : ex: `grown-turtle-32361.upstash.io`
     - **Port** : `6379` (standard Redis)
     - **Password** : Un long token (commence souvent par `AX5...`)
   - Ou utilisez l'URL Redis complète dans l'onglet "Redis CLI" :
     ```
     redis://default:VOTRE_PASSWORD@VOTRE_HOST.upstash.io:6379
     ```

4. **Configurer les variables d'environnement sur Render**
   
   Vous avez deux options :
   
   **Option A : URL complète (Recommandé)**
   ```bash
   REDIS_HOST=redis://default:VOTRE_PASSWORD@VOTRE_HOST.upstash.io:6379
   ```
   
   **Option B : Host/Port séparés**
   ```bash
   REDIS_HOST=VOTRE_HOST.upstash.io
   REDIS_PORT=6379
   REDIS_PASSWORD=VOTRE_PASSWORD
   REDIS_TTL=3600
   ```
   
   ⚠️ **Important** : Upstash utilise TLS. Le client Redis Python le gère automatiquement avec l'URL `redis://`, mais si vous utilisez host/port séparés, vous devrez peut-être utiliser `rediss://` (avec deux 's' pour SSL).

### Option 2 : Redis Cloud (Redis Labs) - Gratuit

**Avantages :**
- 30 MB de stockage gratuit
- Fonctionne avec le client Redis standard

**Étapes :**

1. **Créer un compte Redis Cloud**
   - Aller sur https://redis.com/try-free/
   - Cliquer sur "Start Free"
   - Créer un compte (email ou Google)

2. **Créer une base de données**
   - Dans le dashboard, cliquer sur "New Subscription"
   - Choisir "Fixed" (gratuit)
   - Créer une base de données
   - Noter : **Host**, **Port**, **Password**

3. **Configurer sur Render**
   ```bash
   REDIS_HOST=votre-host.redis.cloud
   REDIS_PORT=12345
   REDIS_PASSWORD=votre-password
   REDIS_TTL=3600
   ```

### Option 3 : Render Redis Service

**Avantages :**
- Intégration native avec Render
- Configuration simple

**Étapes :**

1. **Dans votre dashboard Render**
   - Cliquer sur "New +"
   - Choisir "Redis"
   - Donner un nom (ex: "soilsmart-redis")
   - Plan : "Free" (si disponible) ou "Starter"

2. **Récupérer les variables d'environnement**
   - Render génère automatiquement les variables
   - Elles sont préfixées avec le nom du service (ex: `SOILSMART_REDIS_URL`)

3. **Lier au service web**
   - Dans votre service web (API)
   - Aller dans "Environment"
   - Ajouter les variables Redis (ou les lier automatiquement)

### Option 4 : Redis local (Pour développement)

**Installation :**

**Sur Windows :**
```bash
# Via Chocolatey
choco install redis-64

# Ou télécharger depuis
# https://github.com/microsoftarchive/redis/releases
```

**Sur Linux/Mac :**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Démarrer Redis
redis-server
```

**Configuration locale :**
```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_TTL=3600
```

## 🔧 Configuration sur Render

### Méthode 1 : Variables d'environnement manuelles (Upstash)

1. Aller dans votre service Render → "Environment"
2. Ajouter ces variables :

   **Pour Upstash (Recommandé - URL complète) :**
   ```bash
   REDIS_HOST=redis://default:VOTRE_PASSWORD@VOTRE_HOST.upstash.io:6379
   REDIS_TTL=3600
   ```
   
   **Ou avec Host/Port séparés :**
   ```bash
   REDIS_HOST=VOTRE_HOST.upstash.io
   REDIS_PORT=6379
   REDIS_PASSWORD=VOTRE_PASSWORD
   REDIS_TTL=3600
   ```
   
   ⚠️ **Note** : Remplacez `VOTRE_PASSWORD` et `VOTRE_HOST` par les valeurs réelles de votre compte Upstash.

### Méthode 2 : Variables d'environnement pour Redis standard

1. Aller dans votre service Render → "Environment"
2. Ajouter ces variables :
   ```bash
   REDIS_HOST=votre-host
   REDIS_PORT=6379
   REDIS_PASSWORD=votre-password
   REDIS_TTL=3600
   ```

### Méthode 3 : Lier un service Redis Render

1. Créer un service Redis sur Render
2. Dans votre service API, aller dans "Settings" → "Services"
3. "Link Resource" → Sélectionner votre Redis
4. Les variables seront automatiquement ajoutées

## 🧪 Test de la connexion Redis

Une fois configuré, vous pouvez tester avec l'endpoint de santé :

```bash
GET https://votre-api.render.com/health
```

Réponse attendue :
```json
{
  "status": "ok",
  "cache": "redis"  // ou "memory" si Redis n'est pas disponible
}
```

## 📝 Note importante

**Le cache fonctionne sans Redis !**
- Si Redis n'est pas configuré, l'application utilise un cache mémoire
- Le cache mémoire est limité à 100 entrées par worker
- Les entrées sont partagées entre workers uniquement avec Redis

## 🆘 Dépannage

**Redis non connecté :**
- Vérifier les variables d'environnement
- Vérifier que Redis est accessible (firewall, réseau)
- Consulter les logs : `⚠️ Redis not available, using in-memory cache`

**Performance :**
- Le cache mémoire fonctionne bien pour le développement
- Redis est recommandé pour la production avec plusieurs workers

## 💡 Recommandation

**Pour le développement local :** Redis local ou pas de Redis (cache mémoire)

**Pour la production (Render) :**
1. **Upstash Redis** (recommandé) - Gratuit et facile
2. **Render Redis Service** - Intégration native
3. **Redis Cloud** - 30 MB gratuit

