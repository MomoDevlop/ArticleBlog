# Quick Start Guide

Guide rapide pour démarrer le projet Blog API en 5 minutes.

## Prérequis

- Docker Desktop installé
- 4 GB RAM disponible
- Ports libres: 3000, 4000, 5000, 5432, 5433, 9090, 9092

## Installation en 3 Étapes

### 1. Configuration

```bash
# Copier le fichier d'environnement
cp .env.example .env

# (Optionnel) Éditer .env si nécessaire
```

### 2. Démarrage

```bash
# Construire et démarrer tous les services
docker-compose up -d

# Attendre 30-60 secondes que tous les services soient prêts
```

### 3. Vérification

```bash
# Vérifier que tout fonctionne
./scripts/health_check.sh

# Ou manuellement
curl http://localhost:5000/api/v1/health
curl http://localhost:4000/health
```

## Peupler avec des Données de Test

```bash
# Installer les dépendances Python
pip install requests faker

# Exécuter le script de seed
python scripts/seed_data.py
```

## Accès aux Services

| Service | URL | Identifiants |
|---------|-----|--------------|
| **REST API** | http://localhost:5000 | - |
| **GraphQL Playground** | http://localhost:4000/graphql | - |
| **Prometheus** | http://localhost:9090 | - |
| **Grafana** | http://localhost:3000 | admin/admin |

## Exemples Rapides

### REST API

```bash
# Lister les articles
curl http://localhost:5000/api/v1/articles

# Créer un article
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{"title":"Mon Article","content":"Contenu","author":"Moi"}'

# Rechercher
curl "http://localhost:5000/api/v1/articles/search?q=flask"
```

### GraphQL

Ouvrez http://localhost:4000/graphql et essayez:

```graphql
# Lister les articles
query {
  articles(page: 1, perPage: 5) {
    items {
      id
      title
      author
      status
    }
    pageInfo {
      totalItems
      hasNext
    }
  }
}

# Créer un article
mutation {
  createArticle(input: {
    title: "Test GraphQL"
    content: "Contenu de test"
    author: "Test User"
  }) {
    id
    title
    status
  }
}
```

## Commandes Utiles

```bash
# Voir les logs en temps réel
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f flask-api

# Redémarrer un service
docker-compose restart flask-api

# Arrêter tout
docker-compose down

# Arrêter et supprimer les données
docker-compose down -v
```

## Vérifier la Synchronisation Kafka

```bash
# 1. Créer un article via REST
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Sync","content":"Test","author":"User"}'

# 2. Vérifier dans DB1
docker-compose exec postgres-db1 psql -U blog_user -d blog_db \
  -c "SELECT id, title FROM articles ORDER BY id DESC LIMIT 3;"

# 3. Vérifier dans DB2 (devrait être synchronisé)
docker-compose exec postgres-db2 psql -U blog_user -d blog_replica_db \
  -c "SELECT id, title FROM articles ORDER BY id DESC LIMIT 3;"

# 4. Voir les événements Kafka
docker-compose logs kafka-sync
```

## Problèmes Courants

### Les services ne démarrent pas

```bash
# Vérifier Docker
docker --version

# Vérifier les logs
docker-compose logs

# Reconstruire
docker-compose build --no-cache
docker-compose up -d
```

### Port déjà utilisé

```bash
# Windows
netstat -ano | findstr :5000

# macOS/Linux
lsof -i :5000

# Changer le port dans docker-compose.yml
```

### Kafka ne démarre pas

```bash
# Attendre plus longtemps (Kafka peut prendre 60s)
sleep 60

# Vérifier Zookeeper
docker-compose logs zookeeper

# Redémarrer dans l'ordre
docker-compose stop kafka zookeeper
docker-compose up -d zookeeper
sleep 10
docker-compose up -d kafka
```

## Prochaines Étapes

1.  Lire la [Documentation complète](README.md)
2.  Consulter le [Guide d'Installation](docs/INSTALLATION.md)
3.  Voir la [Documentation API](docs/API_DOCUMENTATION.md)
4.  Explorer Grafana pour voir les métriques
5.  Tester les endpoints avec Postman ou curl

## Support

- Voir les logs: `docker-compose logs -f [service]`
- Health check: `./scripts/health_check.sh`
- Documentation complète: [README.md](README.md)

---

