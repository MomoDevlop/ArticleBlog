# Blog API - RESTful + GraphQL + Kafka Sync

[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![GraphQL](https://img.shields.io/badge/graphql-Strawberry-ff69b4.svg)](https://strawberry.rocks/)
[![Kafka](https://img.shields.io/badge/kafka-3.6-black.svg)](https://kafka.apache.org/)

Un système de gestion d'articles de blog combinant une API RESTful Flask, un gateway GraphQL, et une synchronisation en temps réel entre deux bases de données PostgreSQL via Apache Kafka, avec monitoring Prometheus/Grafana.

## Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation Rapide](#installation-rapide)
- [Utilisation](#utilisation)
- [API Documentation](#api-documentation)
- [Monitoring](#monitoring)
- [Tests](#tests)
- [Structure du Projet](#structure-du-projet)
- [Technologies](#technologies)
- [Contributeurs](#contributeurs)

## Vue d'ensemble

Ce projet est une application de démonstration complète illustrant:
- **API RESTful** avec Flask pour gérer des articles de blog (CRUD)
- **Gateway GraphQL** pour des requêtes flexibles
- **Synchronisation temps réel** via Kafka entre deux bases PostgreSQL
- **Monitoring** avec Prometheus et Grafana
- **Containerisation** complète avec Docker Compose

### Cas d'usage
- Apprentissage des architectures microservices
- Démonstration de synchronisation de bases de données
- Exemple d'intégration REST + GraphQL
- Monitoring et observabilité avec Prometheus

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Architecture Globale                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐  │
│    │ PostgreSQL   │◄───►│    Flask     │◄───►│   GraphQL    │  │
│    │   DB1        │     │  REST API    │     │   Gateway    │  │
│    │  (Primary)   │     │              │     │              │  │
│    └──────┬───────┘     └──────┬───────┘     └──────────────┘  │
│           │                    │                                │
│           │                    │ (publie événements)            │
│           ▼                    ▼                                │
│    ┌──────────────┐     ┌──────────────┐                        │
│    │    Kafka     │     │  Prometheus  │────► Grafana          │
│    │   Broker     │     └──────────────┘                        │
│    └──────┬───────┘                                             │
│           │ (consomme événements)                               │
│           ▼                                                     │
│    ┌──────────────┐                                             │
│    │ PostgreSQL   │                                             │
│    │   DB2        │                                             │
│    │  (Replica)   │                                             │
│    └──────────────┘                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Flux de Données

1. **Client → GraphQL Gateway** : Requête GraphQL
2. **GraphQL → Flask API** : Appel REST HTTP
3. **Flask API → DB1** : Opération CRUD sur base primaire
4. **Flask API → Kafka** : Publication d'événement (article.created, article.updated, etc.)
5. **Kafka → Sync Service** : Consommation d'événement
6. **Sync Service → DB2** : Réplication sur base secondaire
7. **Prometheus** : Scraping des métriques de tous les services

## Fonctionnalités

### API REST Flask
- ✅ CRUD complet sur les articles
- ✅ Pagination et filtrage
- ✅ Recherche full-text
- ✅ Publication d'articles
- ✅ Validation avec Marshmallow
- ✅ Métriques Prometheus

### GraphQL Gateway
- ✅ Queries (article, articles, searchArticles)
- ✅ Mutations (createArticle, updateArticle, deleteArticle, publishArticle)
- ✅ Types fortement typés
- ✅ Filtrage et pagination
- ✅ Playground GraphQL intégré

### Synchronisation Kafka
- ✅ Événements en temps réel
- ✅ Idempotence (évite les doublons)
- ✅ Retry logic avec backoff
- ✅ Gestion des erreurs
- ✅ Logging détaillé

### Monitoring
- ✅ Métriques Prometheus
- ✅ Dashboards Grafana
- ✅ Alerting configuré
- ✅ Health checks

## Prérequis

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**
- Au moins **4 GB RAM** disponible pour Docker

## Installation Rapide

### 1. Cloner le repository

```bash
git clone <URL_DU_REPO>
cd blog-api-graphql-sync
```

### 2. Configuration

```bash
# Copier le fichier d'environnement
cp .env.example .env

# (Optionnel) Modifier les variables d'environnement
nano .env
```

### 3. Démarrage

#### Option A: Avec le script d'installation (recommandé)

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

#### Option B: Manuellement

```bash
# Construire les images
docker-compose build

# Démarrer tous les services
docker-compose up -d

# Vérifier que tout fonctionne
./scripts/health_check.sh
```

### 4. Peupler la base avec des données de test

```bash
# Installer les dépendances pour le script de seed
pip install requests faker

# Exécuter le script
python scripts/seed_data.py
```

## Utilisation

### Accès aux Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Flask REST API | http://localhost:5000 | - |
| GraphQL Playground | http://localhost:4000/graphql | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |

### Exemples d'utilisation

#### REST API

```bash
# Lister tous les articles
curl http://localhost:5000/api/v1/articles

# Créer un article
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mon Premier Article",
    "content": "Contenu de l'\''article...",
    "author": "John Doe",
    "category": "technology",
    "tags": ["api", "rest"]
  }'

# Obtenir un article spécifique
curl http://localhost:5000/api/v1/articles/1

# Publier un article
curl -X POST http://localhost:5000/api/v1/articles/1/publish

# Rechercher des articles
curl "http://localhost:5000/api/v1/articles/search?q=flask"
```

#### GraphQL

```graphql
# Query: Lister les articles
query {
  articles(page: 1, perPage: 10) {
    items {
      id
      title
      author
      category
      status
      createdAt
    }
    pageInfo {
      totalPages
      totalItems
      hasNext
    }
  }
}

# Query: Obtenir un article
query {
  article(id: "1") {
    id
    title
    content
    author
    tags
    viewsCount
  }
}

# Mutation: Créer un article
mutation {
  createArticle(input: {
    title: "GraphQL Tutorial"
    content: "Learn GraphQL basics..."
    author: "Jane Smith"
    category: "programming"
    tags: ["graphql", "api"]
  }) {
    id
    title
    status
  }
}

# Mutation: Publier un article
mutation {
  publishArticle(id: "1") {
    id
    status
    publishedAt
  }
}
```

## API Documentation

### Endpoints REST

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/v1/articles` | Liste tous les articles (pagination, filtres) |
| GET | `/api/v1/articles/{id}` | Récupère un article |
| POST | `/api/v1/articles` | Crée un article |
| PUT | `/api/v1/articles/{id}` | Met à jour un article |
| PATCH | `/api/v1/articles/{id}` | Met à jour partiellement |
| DELETE | `/api/v1/articles/{id}` | Supprime un article |
| POST | `/api/v1/articles/{id}/publish` | Publie un article |
| GET | `/api/v1/articles/search` | Recherche d'articles |
| GET | `/api/v1/health` | Health check |
| GET | `/metrics` | Métriques Prometheus |

### Paramètres de Requête (GET /articles)

- `page` (int): Numéro de page (défaut: 1)
- `per_page` (int): Articles par page (défaut: 10, max: 100)
- `status` (string): Filtrer par statut (draft/published/archived)
- `category` (string): Filtrer par catégorie
- `author` (string): Filtrer par auteur

### Modèle Article

```json
{
  "id": 1,
  "title": "Titre de l'article",
  "content": "Contenu de l'article...",
  "author": "John Doe",
  "category": "technology",
  "tags": ["api", "rest"],
  "status": "published",
  "views_count": 150,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z",
  "published_at": "2024-01-15T14:20:00Z"
}
```

Voir [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md) pour plus de détails.

## Monitoring

### Prometheus

Accéder à Prometheus: http://localhost:9090

**Métriques disponibles:**
- `http_requests_total` - Total des requêtes HTTP
- `http_request_duration_seconds` - Latence des requêtes
- `articles_total` - Nombre d'articles par statut
- `kafka_messages_sent_total` - Messages Kafka envoyés

### Grafana

Accéder à Grafana: http://localhost:3000 (admin/admin)

**Dashboards configurés:**
- Request Rate (req/sec)
- Latency Distribution (p50, p90, p99)
- Error Rate
- Kafka Throughput
- Service Health

## Tests

```bash
# Tests Flask API
docker-compose exec flask-api pytest

# Tests avec coverage
docker-compose exec flask-api pytest --cov=app --cov-report=html

# Tests GraphQL Gateway
docker-compose exec graphql-gateway pytest
```

## Structure du Projet

```
blog-api-graphql-sync/
├── flask-api/               # API RESTful Flask
│   ├── app/
│   │   ├── models/         # Modèles SQLAlchemy
│   │   ├── routes/         # Endpoints API
│   │   ├── services/       # Logique métier
│   │   ├── schemas/        # Validation Marshmallow
│   │   └── utils/          # Métriques Prometheus
│   └── tests/              # Tests unitaires
├── graphql-gateway/        # Gateway GraphQL
│   ├── app/
│   │   ├── schema.py       # Schéma GraphQL
│   │   ├── resolvers/      # Resolvers
│   │   └── clients/        # Client REST
│   └── tests/
├── kafka-sync/             # Service de synchronisation
│   └── app/
│       ├── consumer.py     # Consumer Kafka
│       ├── sync_service.py # Logique sync
│       └── db_connector.py # Connexion DB2
├── monitoring/             # Configuration monitoring
│   ├── prometheus/
│   └── grafana/
├── database/               # Scripts SQL
├── scripts/                # Scripts utilitaires
├── docs/                   # Documentation
├── docker-compose.yml      # Orchestration
├── .env                    # Configuration
└── README.md              # Ce fichier
```

## Technologies

### Backend
- **Flask 3.0** - Framework web Python
- **SQLAlchemy 2.0** - ORM
- **Marshmallow** - Validation et sérialisation
- **Strawberry GraphQL** - Serveur GraphQL
- **FastAPI** - Framework pour GraphQL gateway

### Infrastructure
- **PostgreSQL 15** - Base de données
- **Apache Kafka 3.6** - Streaming d'événements
- **Zookeeper** - Coordination Kafka
- **Docker** - Containerisation

### Monitoring
- **Prometheus** - Métriques
- **Grafana** - Visualisation

## Commandes Utiles

```bash
# Démarrer tous les services
make up

# Arrêter tous les services
make down

# Voir les logs
make logs

# Logs d'un service spécifique
make logs-api
make logs-graphql

# Health check
make health

# Peupler la base de données
make seed

# Tests
make test

# Accéder à la base de données
make db1-shell
make db2-shell

# Voir les topics Kafka
make kafka-topics

# Consommer les messages Kafka
make kafka-consume
```

## Troubleshooting

### Problème: Services ne démarrent pas

```bash
# Vérifier les logs
docker-compose logs

# Redémarrer un service
docker-compose restart [service-name]

# Reconstruire les images
docker-compose build --no-cache
docker-compose up -d
```

### Problème: Kafka ne se connecte pas

```bash
# Vérifier Zookeeper
docker-compose logs zookeeper

# Vérifier Kafka
docker-compose logs kafka

# Attendre que Kafka soit prêt (peut prendre 30-60 secondes)
```

### Problème: Synchronisation DB2 ne fonctionne pas

```bash
# Vérifier le consumer Kafka
docker-compose logs kafka-sync

# Vérifier que DB2 est accessible
docker-compose exec kafka-sync pg_isready -h postgres-db2
```

## Guide d'Installation Détaillé

Voir [docs/INSTALLATION.md](docs/INSTALLATION.md) pour un guide complet.

## Contributeurs

Ce projet a été développé dans le cadre d'un projet académique.

## Licence

Ce projet est à usage éducatif.

## Projet Académique

**Thème:** Création d'une API RESTful avec Flask et Consommation avec GraphQL

**Objectifs:**
- Apprendre à créer une API RESTful avec Flask
- Consommer l'API avec GraphQL
- Synchroniser des bases de données via Kafka
- Implémenter du monitoring avec Prometheus

---

Pour plus d'informations, consultez la [documentation complète](docs/).
