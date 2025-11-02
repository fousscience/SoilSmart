# Guide Rapide : Configuration Upstash Redis pour SoilSmart

## ✅ Étapes Complètes

### 1. Créer une base de données Redis sur Upstash

1. Connectez-vous sur https://console.upstash.com/redis
2. Cliquez sur **"Create Database"**
3. Configurez :
   - **Name** : `soilsmart-cache` (ou autre nom)
   - **Type** : `Redis`
   - **Region** : `Global` (meilleure latence) ou une région spécifique
   - **Plan** : `Free` (plan gratuit)
4. Cliquez sur **"Create"**

### 2. Récupérer les informations de connexion

Une fois la base créée :

1. Cliquez sur votre base de données dans la liste
2. Dans l'onglet **"Details"**, vous verrez :
   - **Endpoint** : ex: `grown-turtle-32361.upstash.io`
   - **Port** : `6379`
   - **Password** : Un long token (ex: `AX5pAAIncDIxMmM1ODUyNDE0YTg0OWIxYjIwOTY0MGJlZTEwODg5OXAyMzIzNjE`)

3. **Ou** dans l'onglet **"Redis CLI"**, vous verrez la commande complète :
   ```
   redis-cli --tls -u redis://default:PASSWORD@HOST.upstash.io:6379
   ```
   Vous pouvez extraire l'URL de cette commande.

### 3. Configurer sur Render

#### Option A : URL Complète (Recommandé)

1. Dans votre dashboard Render, allez dans votre service API
2. Cliquez sur **"Environment"**
3. Ajoutez cette variable :
   ```bash
   REDIS_HOST=redis://default:VOTRE_PASSWORD@VOTRE_HOST.upstash.io:6379
   REDIS_TTL=3600
   ```

   **Exemple avec vos valeurs réelles :**
   ```bash
   REDIS_HOST=redis://default:AX5pAAIncDIxMmM1ODUyNDE0YTg0OWIxYjIwOTY0MGJlZTEwODg5OXAyMzIzNjE@grown-turtle-32361.upstash.io:6379
   REDIS_TTL=3600
   ```

#### Option B : Host/Port séparés

Si vous préférez séparer les valeurs :

```bash
REDIS_HOST=grown-turtle-32361.upstash.io
REDIS_PORT=6379
REDIS_PASSWORD=AX5pAAIncDIxMmM1ODUyNDE0YTg0OWIxYjIwOTY0MGJlZTEwODg5OXAyMzIzNjE
REDIS_TTL=3600
```

### 4. Tester la connexion

Une fois déployé sur Render, testez avec l'endpoint de santé :

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

Si vous voyez `"cache": "memory"`, vérifiez :
- Les variables d'environnement sont bien définies
- Le mot de passe est correct (pas d'espaces)
- Redis est accessible depuis Render

## 🔒 Sécurité

⚠️ **Important** : 
- Ne partagez jamais votre mot de passe Redis publiquement
- Les variables d'environnement sur Render sont sécurisées
- Si votre mot de passe est compromis, régénérez-le dans le dashboard Upstash

## 📝 Notes

- **TLS/SSL** : Upstash utilise TLS par défaut. Le client Redis Python (`redis-py`) gère automatiquement TLS avec l'URL `redis://`.
- **TTL** : Le TTL par défaut est de 1 heure (3600 secondes). Les rapports identiques seront mis en cache pendant 1 heure.
- **Plan Gratuit** : 10 000 commandes/jour, largement suffisant pour le développement et la petite production.

## 🆘 Dépannage

**Connexion échoue :**
- Vérifiez que l'URL est complète et correcte
- Vérifiez que le mot de passe n'a pas d'espaces avant/après
- Vérifiez les logs Render pour voir les erreurs de connexion

**Cache toujours en mémoire :**
- Vérifiez que `REDIS_HOST` est bien défini dans les variables d'environnement Render
- Redéployez votre service après avoir ajouté les variables
- Vérifiez les logs : `⚠️ Redis not available, using in-memory cache`

## ✅ Vérification Finale

Après configuration, vous devriez voir dans les logs Render au démarrage :
```
✅ Redis cache connected
```

Et dans l'endpoint `/health` :
```json
{
  "status": "ok",
  "cache": "redis"
}
```

## 🎉 C'est tout !

Votre application utilise maintenant Redis pour le cache. Les fichiers PDF identiques seront analysés instantanément depuis le cache au lieu de refaire toute l'analyse.

