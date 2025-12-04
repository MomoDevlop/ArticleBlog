# Guide d'Installation Détaillé

Ce guide vous accompagne pas à pas dans l'installation et la configuration du projet Blog API.

## Table des Matières
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Configuration](#configuration)
- [Démarrage](#démarrage)
- [Vérification](#vérification)
- [Accès aux Services](#accès-aux-services)
- [Problèmes Courants](#problèmes-courants)

## Prérequis

### 1. Docker et Docker Compose

**Windows:**
- Télécharger [Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- Installer et redémarrer
- Vérifier: `docker --version` et `docker-compose --version`

**macOS:**
- Télécharger [Docker Desktop for Mac](https://docs.docker.com/desktop/install/mac-install/)
- Installer et démarrer Docker Desktop
- Vérifier: `docker --version` et `docker-compose --version`

**Linux (Ubuntu/Debian):**
```bash
# Installer Docker
sudo apt-get update
sudo apt-get install docker.io docker-compose

# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrer la session
newgrp docker

# Vérifier
docker --version
docker-compose --version
```

### 2. Git

```bash
# Vérifier si Git est installé
git --version

# Si non installé:
# Windows: https://git-scm.com/download/win
# macOS: brew install git
# Linux: sudo apt-get install git
```

### 3. Ressources Système

Assurez-vous d'avoir au moins:
- **RAM:** 4 GB disponible pour Docker
- **Stockage:** 5 GB d'espace disque libre
- **Ports libres:** 3000, 4000, 5000, 5432, 5433, 9090, 9092

## Installation

### Étape 1: Cloner le Repository

```bash
# Cloner le projet
git clone <URL_DU_REPO_GIT>

# Aller dans le répertoire
cd blog-api-graphql-sync

# Vérifier la structure
ls -la
```

### Étape 2: Configuration de l'Environnement

```bash
# Copier le fichier d'environnement exemple
cp .env.example .env

# Éditer le fichier .env (optionnel)
nano .env  # ou vim, code, etc.
```

#### Variables d'environnement importantes:

```env
# Flask
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=CHANGEZ_CETTE_CLE_EN_PRODUCTION

# Base de données 1
DB1_NAME=blog_db
DB1_USER=blog_user
DB1_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE

# Base de données 2
DB2_NAME=blog_replica_db
DB2_USER=blog_user
DB2_PASSWORD=CHANGEZ_CE_MOT_DE_PASSE

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_ARTICLES=article-events
```

### Étape 3: Rendre les Scripts Exécutables (Linux/macOS)

```bash
chmod +x scripts/setup.sh
chmod +x scripts/health_check.sh
```

## Configuration

### Configuration Avancée (Optionnel)

#### Personnaliser les Ports

Éditez `docker-compose.yml` pour changer les ports:

```yaml
services:
  flask-api:
    ports:
      - "5000:5000"  # Changez le premier port si 5000 est déjà utilisé
```

#### Ajuster les Ressources Docker

Si vous avez des contraintes de mémoire:

```yaml
services:
  flask-api:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

## Démarrage

### Méthode 1: Script Automatique (Recommandé)

```bash
./scripts/setup.sh
```

Ce script va:
1. Vérifier les prérequis
2. Créer le fichier .env
3. Construire les images Docker
4. Démarrer tous les services
5. Exécuter les migrations de base de données

### Méthode 2: Manuel

```bash
# 1. Construire les images
docker-compose build

# 2. Démarrer les services
docker-compose up -d

# 3. Attendre que les services soient prêts (30-60 secondes)
sleep 30

# 4. Vérifier les logs
docker-compose logs -f
```

## Vérification

### 1. Vérifier que tous les services sont démarrés

```bash
# Option 1: Avec le script
./scripts/health_check.sh

# Option 2: Manuellement
docker-compose ps
```

Vous devriez voir tous les services avec le statut "Up":
```
NAME                      STATUS
blog-postgres-db1         Up
blog-postgres-db2         Up
blog-zookeeper            Up
blog-kafka                Up
blog-flask-api            Up
blog-graphql-gateway      Up
blog-kafka-sync           Up
blog-prometheus           Up
blog-grafana              Up
```

### 2. Tester les Endpoints

```bash
# Flask API Health Check
curl http://localhost:5000/api/v1/health

# GraphQL Health Check
curl http://localhost:4000/health

# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health
```

### 3. Peupler la Base avec des Données de Test

```bash
# Installer les dépendances Python pour le script
pip install requests faker

# Exécuter le script de seed
python scripts/seed_data.py
```

### 4. Vérifier la Synchronisation Kafka

```bash
# Voir les logs du service de synchronisation
docker-compose logs -f kafka-sync

# Créer un article via l'API REST
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Sync",
    "content": "Test de synchronisation",
    "author": "Test User"
  }'

# Vérifier que l'article apparaît dans DB2
docker-compose exec postgres-db2 psql -U blog_user -d blog_replica_db \
  -c "SELECT id, title FROM articles ORDER BY id DESC LIMIT 5;"
```

## Accès aux Services

Une fois tous les services démarrés, vous pouvez y accéder:

### Web Interfaces

| Service | URL | Credentials |
|---------|-----|-------------|
| Flask REST API | http://localhost:5000 | - |
| API Documentation | http://localhost:5000/ | - |
| GraphQL Playground | http://localhost:4000/graphql | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |

### Base de Données

```bash
# Se connecter à PostgreSQL DB1
docker-compose exec postgres-db1 psql -U blog_user -d blog_db

# Se connecter à PostgreSQL DB2
docker-compose exec postgres-db2 psql -U blog_user -d blog_replica_db
```

### Kafka

```bash
# Lister les topics Kafka
docker-compose exec kafka kafka-topics \
  --list \
  --bootstrap-server localhost:9092

# Consommer les messages (depuis le début)
docker-compose exec kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic article-events \
  --from-beginning
```

## Problèmes Courants

### Problème 1: Port déjà utilisé

**Erreur:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:5000: bind: address already in use
```

**Solution:**
```bash
# Trouver le processus utilisant le port
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Arrêter le processus ou changer le port dans docker-compose.yml
```

### Problème 2: Kafka ne démarre pas

**Erreur:**
```
kafka    | ERROR Fatal error during KafkaServer startup
```

**Solution:**
```bash
# Kafka nécessite Zookeeper, vérifier qu'il est démarré
docker-compose logs zookeeper

# Redémarrer dans l'ordre
docker-compose stop kafka zookeeper
docker-compose up -d zookeeper
sleep 10
docker-compose up -d kafka
```

### Problème 3: Erreur de connexion à la base de données

**Erreur:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps postgres-db1

# Vérifier les logs
docker-compose logs postgres-db1

# Redémarrer le service
docker-compose restart postgres-db1
docker-compose restart flask-api
```

### Problème 4: Mémoire insuffisante

**Erreur:**
```
Error: Cannot start service X: OCI runtime create failed
```

**Solution:**
```bash
# Augmenter la mémoire allouée à Docker
# Docker Desktop > Settings > Resources > Memory : 4GB minimum

# Ou réduire le nombre de services en cours d'exécution
docker-compose up -d postgres-db1 kafka flask-api
```

### Problème 5: Permissions Linux

**Erreur:**
```
permission denied while trying to connect to the Docker daemon socket
```

**Solution:**
```bash
# Ajouter votre utilisateur au groupe docker
sudo usermod -aG docker $USER

# Redémarrer la session ou exécuter
newgrp docker
```

## Commandes de Maintenance

### Arrêter les Services

```bash
# Arrêter sans supprimer les volumes
docker-compose down

# Arrêter et supprimer les volumes (ATTENTION: perte de données)
docker-compose down -v
```

### Redémarrer un Service

```bash
# Redémarrer un service spécifique
docker-compose restart flask-api
docker-compose restart graphql-gateway
```

### Voir les Logs

```bash
# Tous les services
docker-compose logs -f

# Service spécifique
docker-compose logs -f flask-api

# Dernières 100 lignes
docker-compose logs --tail=100 kafka-sync
```

### Reconstruire les Images

```bash
# Reconstruire toutes les images
docker-compose build --no-cache

# Reconstruire une image spécifique
docker-compose build --no-cache flask-api
```

### Nettoyer Docker

```bash
# Supprimer les conteneurs arrêtés
docker container prune

# Supprimer les images inutilisées
docker image prune

# Nettoyer complètement (ATTENTION)
docker system prune -a --volumes
```

## Prochaines Étapes

Une fois l'installation terminée et vérifiée:

1. **Consulter la documentation API**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
2. **Tester les endpoints REST**: Utiliser Postman ou curl
3. **Explorer GraphQL**: Ouvrir http://localhost:4000/graphql
4. **Configurer Grafana**: Créer vos propres dashboards
5. **Modifier le code**: Apporter vos propres améliorations

Pour toute question ou problème non résolu, consultez les logs détaillés avec `docker-compose logs -f [service]`.
