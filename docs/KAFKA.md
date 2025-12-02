# Guide Kafka - Production et Consommation d'Événements

Ce document explique comment tester et vérifier le système de synchronisation en temps réel basé sur Apache Kafka dans le projet Blog API.

## Table des Matières

- [Architecture Kafka](#architecture-kafka)
- [Types d'Événements](#types-dévénements)
- [Tester la Production d'Événements](#tester-la-production-dévénements)
- [Tester la Consommation d'Événements](#tester-la-consommation-dévénements)
- [Vérifier la Synchronisation DB1 → DB2](#vérifier-la-synchronisation-db1--db2)
- [Tests Manuels avec Kafka CLI](#tests-manuels-avec-kafka-cli)
- [Monitoring et Debugging](#monitoring-et-debugging)
- [Résolution de Problèmes](#résolution-de-problèmes)

---

## Architecture Kafka

### Flux de Données

```
┌─────────────────┐        ┌──────────────┐        ┌─────────────────┐
│   Flask API     │        │    Kafka     │        │  Kafka Sync     │
│   (Producer)    │───────>│    Broker    │───────>│  (Consumer)     │
│                 │        │              │        │                 │
│  PostgreSQL DB1 │        │ Topic:       │        │  PostgreSQL DB2 │
│  (Primary)      │        │ articles     │        │  (Replica)      │
└─────────────────┘        └──────────────┘        └─────────────────┘
```

### Composants

1. **Producer (Flask API)** : Publie des événements lorsqu'un article est créé/modifié/supprimé
2. **Kafka Broker** : Stocke les événements dans le topic `articles`
3. **Consumer (Kafka Sync)** : Consomme les événements et met à jour DB2
4. **DB1 (Primary)** : Base de données principale modifiée par l'API REST
5. **DB2 (Replica)** : Base de données répliquée via Kafka

---

## Types d'Événements

Le système gère **4 types d'événements** :

### 1. Article Created (`article.created`)

**Déclenché par :** `POST /api/v1/articles`

**Structure de l'événement :**
```json
{
  "event_type": "article.created",
  "timestamp": "2024-12-02T10:30:45.123456",
  "data": {
    "id": 5,
    "title": "New Article",
    "content": "Article content...",
    "author": "John Doe",
    "category": "technology",
    "tags": ["python", "kafka"],
    "status": "draft",
    "views_count": 0,
    "created_at": "2024-12-02T10:30:45.123456",
    "updated_at": "2024-12-02T10:30:45.123456",
    "published_at": null
  }
}
```

**Action dans Consumer :** Insère un nouvel article dans DB2

---

### 2. Article Updated (`article.updated`)

**Déclenché par :** `PUT /api/v1/articles/{id}` ou `PATCH /api/v1/articles/{id}`

**Structure de l'événement :**
```json
{
  "event_type": "article.updated",
  "timestamp": "2024-12-02T10:35:20.654321",
  "data": {
    "id": 5,
    "title": "Updated Article Title",
    "content": "Updated content...",
    "author": "John Doe",
    "category": "technology",
    "tags": ["python", "kafka", "updated"],
    "status": "draft",
    "views_count": 3,
    "created_at": "2024-12-02T10:30:45.123456",
    "updated_at": "2024-12-02T10:35:20.654321",
    "published_at": null
  }
}
```

**Action dans Consumer :** Met à jour l'article existant dans DB2

---

### 3. Article Published (`article.published`)

**Déclenché par :** `POST /api/v1/articles/{id}/publish`

**Structure de l'événement :**
```json
{
  "event_type": "article.published",
  "timestamp": "2024-12-02T10:40:15.789012",
  "data": {
    "id": 5,
    "title": "Updated Article Title",
    "content": "Updated content...",
    "author": "John Doe",
    "category": "technology",
    "tags": ["python", "kafka", "updated"],
    "status": "published",
    "views_count": 3,
    "created_at": "2024-12-02T10:30:45.123456",
    "updated_at": "2024-12-02T10:40:15.789012",
    "published_at": "2024-12-02T10:40:15.789012"
  }
}
```

**Action dans Consumer :** Met à jour le statut et la date de publication dans DB2

---

### 4. Article Deleted (`article.deleted`)

**Déclenché par :** `DELETE /api/v1/articles/{id}`

**Structure de l'événement :**
```json
{
  "event_type": "article.deleted",
  "timestamp": "2024-12-02T10:45:30.456789",
  "data": {
    "id": 5,
    "title": "Updated Article Title",
    "content": "Updated content...",
    "author": "John Doe",
    "category": "technology",
    "tags": ["python", "kafka", "updated"],
    "status": "published",
    "views_count": 3,
    "created_at": "2024-12-02T10:30:45.123456",
    "updated_at": "2024-12-02T10:40:15.789012",
    "published_at": "2024-12-02T10:40:15.789012"
  }
}
```

**Action dans Consumer :** Supprime l'article de DB2

---

## Tester la Production d'Événements

### Méthode 1 : Via les Logs du Producer (Flask API)

**1. Suivre les logs en temps réel :**
```bash
docker-compose logs -f flask-api
```

**2. Créer un article :**
```bash
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Kafka Event",
    "content": "Testing event production",
    "author": "Kafka Tester"
  }'
```

**3. Vérifier dans les logs :**
```
flask-api | INFO - Article created successfully: ID=6, Title=Test Kafka Event
flask-api | INFO - Publishing to Kafka: topic=articles, event_type=article.created
flask-api | INFO - Event published successfully to Kafka
```

---

### Méthode 2 : Via Kafka Console Consumer

**1. Accéder au container Kafka :**
```bash
docker exec -it blog-kafka bash
```

**2. Lancer le consumer en temps réel :**
```bash
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic articles \
  --from-beginning \
  --property print.timestamp=true \
  --property print.key=true
```

**3. Dans un autre terminal, créer un article :**
```bash
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Real-time Kafka Test",
    "content": "Watch the consumer!",
    "author": "Test User"
  }'
```

**4. Observer l'événement dans le consumer :**
```
CreateTime:1733140845123	null	{"event_type":"article.created","timestamp":"2024-12-02T10:30:45.123456","data":{"id":7,"title":"Real-time Kafka Test",...}}
```

---

### Méthode 3 : Via les Métriques Prometheus

**1. Accéder aux métriques :**
```bash
curl http://localhost:5000/api/v1/metrics | grep kafka_messages_sent
```

**2. Résultat attendu :**
```
# HELP kafka_messages_sent_total Total Kafka messages sent
# TYPE kafka_messages_sent_total counter
kafka_messages_sent_total{event_type="article.created"} 5.0
kafka_messages_sent_total{event_type="article.updated"} 3.0
kafka_messages_sent_total{event_type="article.deleted"} 1.0
kafka_messages_sent_total{event_type="article.published"} 2.0
```

---

## Tester la Consommation d'Événements

### Méthode 1 : Via les Logs du Consumer (Kafka Sync)

**1. Suivre les logs en temps réel :**
```bash
docker-compose logs -f kafka-sync
```

**2. Créer un article via l'API :**
```bash
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sync Test Article",
    "content": "Testing DB synchronization",
    "author": "Sync Tester",
    "category": "testing"
  }'
```

**3. Observer la consommation dans les logs :**
```
kafka-sync | INFO - Received event: article.created for article ID: 8
kafka-sync | INFO - Processing article.created event
kafka-sync | INFO - Event ID: abc123def456... (MD5 hash)
kafka-sync | INFO - Checking idempotency for event ID: abc123def456...
kafka-sync | INFO - Event not processed yet, proceeding...
kafka-sync | INFO - Creating article in DB2: Sync Test Article
kafka-sync | INFO - Article created successfully in DB2
kafka-sync | INFO - Marking event as processed: abc123def456...
kafka-sync | INFO - Successfully processed event: article.created for article 8
kafka-sync | INFO - Committing offset...
```

---

### Méthode 2 : Vérifier la Table `processed_events`

**1. Connecter à DB2 :**
```bash
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica
```

**2. Voir les événements traités :**
```sql
SELECT
  event_id,
  event_type,
  article_id,
  processed_at
FROM processed_events
ORDER BY processed_at DESC
LIMIT 10;
```

**3. Résultat attendu :**
```
           event_id           |   event_type    | article_id |       processed_at
------------------------------+-----------------+------------+---------------------------
 abc123def456...              | article.created |          8 | 2024-12-02 10:30:45.123456
 def789ghi012...              | article.updated |          5 | 2024-12-02 10:25:30.654321
```

---

### Méthode 3 : Test d'Idempotence

L'idempotence garantit qu'un événement traité deux fois n'aura pas d'effet secondaire.

**1. Publier manuellement le même événement deux fois :**
```bash
# Accéder au container Kafka
docker exec -it blog-kafka bash

# Publier un événement manuellement
echo '{"event_type":"article.created","timestamp":"2024-12-02T10:00:00","data":{"id":999,"title":"Duplicate Test","content":"Testing idempotency","author":"Test","category":"test","tags":[],"status":"draft","views_count":0,"created_at":"2024-12-02T10:00:00","updated_at":"2024-12-02T10:00:00","published_at":null}}' | \
kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic articles
```

**2. Observer les logs du consumer :**
```
kafka-sync | INFO - Received event: article.created for article ID: 999
kafka-sync | INFO - Event ID: xyz789abc123...
kafka-sync | INFO - Checking idempotency for event ID: xyz789abc123...
kafka-sync | INFO - Event not processed yet, proceeding...
kafka-sync | INFO - Article created successfully in DB2
```

**3. Publier le même événement une 2ème fois :**
```bash
# Même commande qu'avant
echo '{"event_type":"article.created",...}' | kafka-console-producer ...
```

**4. Vérifier que l'événement est ignoré :**
```
kafka-sync | INFO - Received event: article.created for article ID: 999
kafka-sync | INFO - Event ID: xyz789abc123...
kafka-sync | INFO - Checking idempotency for event ID: xyz789abc123...
kafka-sync | WARNING - Event already processed: xyz789abc123. Skipping...
kafka-sync | INFO - Successfully processed event (already done): article.created for article 999
```

**5. Vérifier qu'il n'y a pas de doublon dans DB2 :**
```sql
SELECT COUNT(*) FROM articles WHERE id = 999;
-- Résultat : 1 (pas de doublon !)
```

---

## Vérifier la Synchronisation DB1 → DB2

### Test Complet du Cycle de Vie

**1. État initial - Vérifier DB1 et DB2 :**
```bash
# DB1
docker exec -it blog-postgres-db1 psql -U bloguser -d blogdb -c "SELECT COUNT(*) FROM articles;"

# DB2
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c "SELECT COUNT(*) FROM articles;"
```

**2. Créer un article dans DB1 (via API) :**
```bash
ARTICLE_ID=$(curl -s -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sync Verification Article",
    "content": "Testing full synchronization",
    "author": "Sync Test",
    "category": "sync-test",
    "tags": ["sync", "test", "kafka"]
  }' | jq -r '.id')

echo "Article créé avec ID: $ARTICLE_ID"
```

**3. Attendre 2-3 secondes pour la synchronisation :**
```bash
sleep 3
```

**4. Vérifier dans DB2 :**
```bash
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c \
  "SELECT id, title, author, category, status FROM articles WHERE title = 'Sync Verification Article';"
```

**Résultat attendu :**
```
 id |          title          |   author   |  category  | status
----+-------------------------+------------+------------+--------
 10 | Sync Verification Article| Sync Test  | sync-test  | draft
```

**5. Mettre à jour l'article :**
```bash
curl -X PUT http://localhost:5000/api/v1/articles/$ARTICLE_ID \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Sync Verification Article - UPDATED",
    "content": "Updated content",
    "author": "Sync Test",
    "category": "sync-test-updated",
    "tags": ["sync", "test", "kafka", "updated"]
  }'

sleep 3
```

**6. Vérifier la mise à jour dans DB2 :**
```bash
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c \
  "SELECT id, title, category FROM articles WHERE id = $ARTICLE_ID;"
```

**Résultat attendu :**
```
 id |              title                  |      category
----+-------------------------------------+--------------------
 10 | Sync Verification Article - UPDATED | sync-test-updated
```

**7. Publier l'article :**
```bash
curl -X POST http://localhost:5000/api/v1/articles/$ARTICLE_ID/publish
sleep 3
```

**8. Vérifier le statut dans DB2 :**
```bash
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c \
  "SELECT id, status, published_at FROM articles WHERE id = $ARTICLE_ID;"
```

**Résultat attendu :**
```
 id | status    |       published_at
----+-----------+---------------------------
 10 | published | 2024-12-02 10:45:30.123456
```

**9. Supprimer l'article :**
```bash
curl -X DELETE http://localhost:5000/api/v1/articles/$ARTICLE_ID
sleep 3
```

**10. Vérifier la suppression dans DB2 :**
```bash
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c \
  "SELECT COUNT(*) FROM articles WHERE id = $ARTICLE_ID;"
```

**Résultat attendu :**
```
 count
-------
     0
```

**Synchronisation complète vérifiée !**

---

## Tests Manuels avec Kafka CLI

### Lister les Topics

```bash
docker exec -it blog-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --list
```

**Résultat attendu :**
```
articles
```

---

### Voir les Détails d'un Topic

```bash
docker exec -it blog-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic articles
```

**Résultat attendu :**
```
Topic: articles
PartitionCount: 1
ReplicationFactor: 1
Configs:
  Topic: articles  Partition: 0  Leader: 1  Replicas: 1  Isr: 1
```

---

### Voir le Lag du Consumer

Le lag indique combien de messages sont en attente de traitement.

```bash
docker exec -it blog-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group blog-sync-group
```

**Résultat attendu (lag = 0 si tout est à jour) :**
```
GROUP           TOPIC    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
blog-sync-group articles 0          45              45              0
```

- **CURRENT-OFFSET** : Dernier message consommé
- **LOG-END-OFFSET** : Dernier message produit
- **LAG** : Messages en attente (doit être 0 ou très faible)

---

### Consommer les Messages depuis le Début

```bash
docker exec -it blog-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic articles \
  --from-beginning \
  --max-messages 10
```

---

### Consommer en Temps Réel

```bash
docker exec -it blog-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic articles
```

Laissez cette commande tourner et créez un article dans un autre terminal.

---

### Produire un Événement Manuellement

**1. Accéder au container :**
```bash
docker exec -it blog-kafka bash
```

**2. Lancer le producer interactif :**
```bash
kafka-console-producer \
  --bootstrap-server localhost:9092 \
  --topic articles
```

**3. Entrer un événement JSON :**
```json
{"event_type":"article.created","timestamp":"2024-12-02T12:00:00","data":{"id":999,"title":"Manual Event","content":"Testing manual production","author":"Manual Tester","category":"test","tags":[],"status":"draft","views_count":0,"created_at":"2024-12-02T12:00:00","updated_at":"2024-12-02T12:00:00","published_at":null}}
```

**4. Appuyer sur ENTER et vérifier les logs du consumer.**

---

## Monitoring et Debugging

### 1. Dashboard Grafana

**Accéder à Grafana :**
```
http://localhost:3000
Identifiants : admin / admin
```

**Métriques Kafka disponibles :**
- `kafka_messages_sent_total` - Nombre de messages publiés par type
- Graphique de distribution par `event_type`

---

### 2. Métriques Prometheus

**Accéder à Prometheus :**
```
http://localhost:9090
```

**Requêtes utiles :**

**Total de messages Kafka envoyés :**
```promql
sum(kafka_messages_sent_total)
```

**Messages par type d'événement :**
```promql
kafka_messages_sent_total
```

**Taux de messages par seconde :**
```promql
rate(kafka_messages_sent_total[5m])
```

---

### 3. Logs Détaillés

**Activer les logs DEBUG (optionnel) :**

Modifier `kafka-sync/app/main.py` :
```python
logging.basicConfig(
    level=logging.DEBUG,  # Change INFO to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Redémarrer le service :
```bash
docker-compose restart kafka-sync
```

---

### 4. Vérifier la Santé des Services

```bash
# Tous les services
docker-compose ps

# Kafka Broker
docker exec -it blog-kafka kafka-broker-api-versions --bootstrap-server localhost:9092

# Zookeeper
docker exec -it blog-zookeeper zkServer.sh status
```

---

## Résolution de Problèmes

### Problème 1 : Les événements ne sont pas produits

**Symptômes :**
- Aucun log de publication dans Flask API
- Aucun événement dans `kafka-console-consumer`

**Solutions :**

**1. Vérifier que Kafka est UP :**
```bash
docker-compose ps kafka
```

**2. Vérifier la connexion depuis Flask :**
```bash
docker-compose logs flask-api | grep -i kafka
```

**3. Tester la connexion manuellement :**
```bash
docker exec -it blog-flask-api python3 -c "
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka:9092')
print('Connection OK')
"
```

**4. Vérifier la variable d'environnement :**
```bash
docker exec -it blog-flask-api env | grep KAFKA
```

---

### Problème 2 : Les événements ne sont pas consommés

**Symptômes :**
- Les événements apparaissent dans Kafka
- Mais DB2 n'est pas mis à jour
- Lag du consumer augmente

**Solutions :**

**1. Vérifier que kafka-sync est UP :**
```bash
docker-compose ps kafka-sync
```

**2. Voir les logs d'erreur :**
```bash
docker-compose logs kafka-sync | grep -i error
```

**3. Vérifier la connexion à DB2 :**
```bash
docker exec -it blog-kafka-sync python3 -c "
import psycopg2
conn = psycopg2.connect('postgresql://bloguser:blogpass@postgres-db2:5432/blogdb_replica')
print('DB2 Connection OK')
"
```

**4. Redémarrer le consumer :**
```bash
docker-compose restart kafka-sync
```

---

### Problème 3 : Événements dupliqués dans DB2

**Symptômes :**
- Un article existe en double dans DB2
- La table `processed_events` n'enregistre pas les IDs

**Solutions :**

**1. Vérifier la table d'idempotence :**
```sql
SELECT COUNT(*) FROM processed_events;
```

**2. Vérifier les contraintes :**
```sql
\d processed_events
-- Doit avoir une UNIQUE constraint sur event_id
```

**3. Recréer la table si nécessaire :**
```sql
DROP TABLE IF EXISTS processed_events;
CREATE TABLE processed_events (
    event_id VARCHAR(255) PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    article_id INTEGER,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

### Problème 4 : Lag du consumer élevé

**Symptômes :**
```
LAG = 1000+
```

**Solutions :**

**1. Augmenter le nombre de workers (si nécessaire) :**

Modifier `docker-compose.yml` pour le consumer :
```yaml
kafka-sync:
  environment:
    KAFKA_CONSUMER_THREADS: 3  # Ajouter cette variable
```

**2. Augmenter le `max_poll_records` :**

Dans `kafka-sync/app/consumer.py` :
```python
consumer = KafkaConsumer(
    # ...
    max_poll_records=100  # Augmenter de 10 à 100
)
```

**3. Vérifier les performances de DB2 :**
```sql
-- Voir les requêtes lentes
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

---

### Problème 5 : Topic `articles` introuvable

**Symptômes :**
```
KafkaError: Topic 'articles' not found
```

**Solutions :**

**1. Créer le topic manuellement :**
```bash
docker exec -it blog-kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create \
  --topic articles \
  --partitions 1 \
  --replication-factor 1
```

**2. Vérifier la variable d'environnement :**
```bash
docker exec -it blog-flask-api env | grep KAFKA_TOPIC
```

---

## Scénarios de Test Académique

### Scénario 1 : Démonstration Complète

**Objectif :** Montrer la synchronisation en temps réel

```bash
# Terminal 1 : Logs du producer
docker-compose logs -f flask-api

# Terminal 2 : Logs du consumer
docker-compose logs -f kafka-sync

# Terminal 3 : Consumer Kafka temps réel
docker exec -it blog-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic articles

# Terminal 4 : Créer un article
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Real-time Sync Demo",
    "content": "Watch all 3 terminals!",
    "author": "Demo User"
  }'
```

Observer en temps réel :
1. Terminal 1 : Flask publie l'événement
2. Terminal 3 : Kafka reçoit l'événement
3. Terminal 2 : Consumer traite et insère dans DB2

---

### Scénario 2 : Test de Résilience

**Objectif :** Vérifier que les événements sont rejouables

```bash
# 1. Arrêter le consumer
docker-compose stop kafka-sync

# 2. Créer plusieurs articles
for i in {1..5}; do
  curl -X POST http://localhost:5000/api/v1/articles \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"Article $i\",\"content\":\"Content $i\",\"author\":\"Test\"}"
  sleep 1
done

# 3. Vérifier le lag
docker exec -it blog-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group blog-sync-group
# LAG doit être = 5

# 4. Redémarrer le consumer
docker-compose start kafka-sync

# 5. Attendre 10 secondes
sleep 10

# 6. Vérifier que le lag est à 0
docker exec -it blog-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --describe \
  --group blog-sync-group
# LAG doit être = 0

# 7. Vérifier que les 5 articles sont dans DB2
docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c \
  "SELECT COUNT(*) FROM articles WHERE author = 'Test';"
# Résultat : 5
```

**Résilience démontrée !**

---

### Scénario 3 : Test de Performance

**Objectif :** Mesurer le débit de synchronisation

```bash
# 1. Créer 100 articles rapidement
time for i in {1..100}; do
  curl -s -X POST http://localhost:5000/api/v1/articles \
    -H "Content-Type: application/json" \
    -d "{\"title\":\"Perf Test $i\",\"content\":\"Content\",\"author\":\"PerfTest\"}" > /dev/null
done

# 2. Attendre que le consumer rattrape
sleep 30

# 3. Vérifier la synchronisation
docker exec -it blog-postgres-db1 psql -U bloguser -d blogdb -c \
  "SELECT COUNT(*) FROM articles WHERE author = 'PerfTest';" > /tmp/db1_count.txt

docker exec -it blog-postgres-db2 psql -U bloguser -d blogdb_replica -c \
  "SELECT COUNT(*) FROM articles WHERE author = 'PerfTest';" > /tmp/db2_count.txt

diff /tmp/db1_count.txt /tmp/db2_count.txt
# Pas de différence = synchronisation parfaite !
```

---

## Ressources Supplémentaires

- [Documentation Apache Kafka](https://kafka.apache.org/documentation/)
- [Kafka Python Client](https://kafka-python.readthedocs.io/)
- [Architecture Event-Driven](https://martinfowler.com/articles/201701-event-driven.html)

---

## Checklist de Validation

Avant de soumettre votre projet, vérifiez :

- [ ] Les 4 types d'événements sont produits correctement
- [ ] Les événements sont consommés sans erreur
- [ ] DB1 et DB2 sont synchronisées
- [ ] L'idempotence fonctionne (pas de doublons)
- [ ] Le lag du consumer est à 0
- [ ] Les logs ne contiennent pas d'erreurs
- [ ] Les métriques Prometheus sont exposées
- [ ] Le dashboard Grafana affiche les événements Kafka

---

**Bonne chance avec votre projet !**
