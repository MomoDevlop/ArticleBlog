# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a microservices-based blog API system combining RESTful and GraphQL architectures with real-time database synchronization.

**Tech Stack:**
- **Flask** - RESTful API for blog articles (CRUD operations)
- **GraphQL Gateway** - Query layer consuming the Flask REST API
- **Kafka** - Event streaming for database synchronization
- **PostgreSQL** - Two databases (primary + replica synchronized via Kafka)
- **Prometheus + Grafana** - Performance monitoring and metrics
- **Docker Compose** - Service orchestration

**Core Functionality:**
- Manage blog articles (create, read, update, delete, publish)
- GraphQL interface for flexible queries
- Real-time synchronization between two PostgreSQL databases via Kafka events
- Comprehensive monitoring with Prometheus metrics

## Architecture

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│ PostgreSQL  │◄───►│   Flask     │◄───►│   GraphQL    │
│   (DB1)     │     │  REST API   │     │   Gateway    │
└──────┬──────┘     └──────┬──────┘     └──────────────┘
       │                   │
       │                   │ (publishes events)
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│    Kafka    │     │ Prometheus  │───► Grafana Dashboard
│   Broker    │     └─────────────┘
└──────┬──────┘
       │ (consumes events)
       ▼
┌─────────────┐
│ PostgreSQL  │
│   (DB2)     │
└─────────────┘
```

## Project Structure

```
blog-api-graphql-sync/
├── flask-api/              # RESTful API service
│   ├── app/
│   │   ├── models/         # SQLAlchemy models (Article)
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic + Kafka producer
│   │   ├── schemas/        # Marshmallow validation schemas
│   │   └── utils/          # Prometheus metrics
│   ├── migrations/         # Alembic database migrations
│   ├── tests/              # Unit and integration tests
│   └── run.py              # Entry point
│
├── graphql-gateway/        # GraphQL service
│   ├── app/
│   │   ├── schema.py       # GraphQL schema (types, queries, mutations)
│   │   ├── resolvers/      # Query/mutation resolvers
│   │   └── clients/        # HTTP client for Flask API
│   └── run.py
│
├── kafka-sync/             # Database synchronization service
│   ├── app/
│   │   ├── consumer.py     # Kafka consumer
│   │   ├── sync_service.py # DB2 synchronization logic
│   │   └── db_connector.py # PostgreSQL DB2 connection
│   └── run.py
│
├── monitoring/
│   ├── prometheus/         # Prometheus configuration
│   └── grafana/            # Grafana dashboards
│
├── database/               # SQL initialization scripts
├── scripts/                # Utility scripts (setup, seed data, health check)
├── docs/                   # Documentation
└── docker-compose.yml      # Service orchestration
```

## Common Commands

### Development Setup

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f [service-name]
docker-compose logs -f flask-api
docker-compose logs -f graphql-gateway
docker-compose logs -f kafka-sync

# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Rebuild specific service
docker-compose build flask-api
docker-compose up -d flask-api
```

### Database Management

```bash
# Run Flask migrations
docker-compose exec flask-api flask db init
docker-compose exec flask-api flask db migrate -m "Initial migration"
docker-compose exec flask-api flask db upgrade

# Access PostgreSQL DB1
docker-compose exec postgres-db1 psql -U blog_user -d blog_db

# Access PostgreSQL DB2
docker-compose exec postgres-db2 psql -U blog_user -d blog_replica_db

# Seed test data
docker-compose exec flask-api python scripts/seed_data.py
```

### Testing

```bash
# Run all Flask tests
docker-compose exec flask-api pytest

# Run specific test file
docker-compose exec flask-api pytest tests/test_articles.py

# Run with coverage
docker-compose exec flask-api pytest --cov=app --cov-report=html

# Run GraphQL tests
docker-compose exec graphql-gateway pytest

# Run integration tests
docker-compose exec flask-api pytest tests/test_integration.py -v
```

### API Testing

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Create article (REST)
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Content","author":"John"}'

# Get articles (REST)
curl http://localhost:5000/api/v1/articles

# GraphQL query
curl -X POST http://localhost:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ articles(page:1,perPage:10) { items { id title author } } }"}'

# View Prometheus metrics
curl http://localhost:5000/metrics
```

### Monitoring

```bash
# Access Grafana dashboard
# URL: http://localhost:3000
# Default credentials: admin/admin

# Access Prometheus UI
# URL: http://localhost:9090

# Check service health
./scripts/health_check.sh
```

## Article Model

The core data model with fields:
- `id` - Primary key
- `title` - Article title (max 200 chars)
- `content` - Article body (text)
- `author` - Author name (max 100 chars)
- `category` - Category (default: 'general')
- `tags` - JSON array of tags
- `status` - Enum: 'draft', 'published', 'archived'
- `views_count` - View counter
- `created_at`, `updated_at`, `published_at` - Timestamps

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/articles` | List articles (supports pagination, filtering) |
| GET | `/api/v1/articles/<id>` | Get single article |
| POST | `/api/v1/articles` | Create article |
| PUT | `/api/v1/articles/<id>` | Update article (full) |
| PATCH | `/api/v1/articles/<id>` | Update article (partial) |
| DELETE | `/api/v1/articles/<id>` | Delete article |
| POST | `/api/v1/articles/<id>/publish` | Publish article |
| GET | `/api/v1/articles/search` | Search articles |
| GET | `/api/v1/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

**Query Parameters for GET /articles:**
- `page` - Page number (default: 1)
- `per_page` - Items per page (default: 10)
- `status` - Filter by status (draft/published/archived)
- `category` - Filter by category
- `author` - Filter by author

## GraphQL Schema

**Main Types:**
```graphql
type Article {
  id: ID!
  title: String!
  content: String!
  author: String!
  category: String
  tags: [String]
  status: ArticleStatus!
  viewsCount: Int
  createdAt: DateTime!
  updatedAt: DateTime
  publishedAt: DateTime
}

enum ArticleStatus { DRAFT, PUBLISHED, ARCHIVED }
```

**Queries:**
```graphql
article(id: ID!): Article
articles(page: Int, perPage: Int, filter: ArticleFilterInput): ArticleConnection!
searchArticles(query: String!): [Article!]!
```

**Mutations:**
```graphql
createArticle(input: ArticleInput!): Article!
updateArticle(id: ID!, input: ArticleUpdateInput!): Article!
deleteArticle(id: ID!): Boolean!
publishArticle(id: ID!): Article!
```

## Kafka Event-Driven Synchronization

**Topic:** `article-events`

**Event Types:**
- `article.created` - Published when an article is created
- `article.updated` - Published when an article is updated
- `article.deleted` - Published when an article is deleted
- `article.published` - Published when an article is published

**Event Message Format:**
```json
{
  "event_type": "article.created",
  "timestamp": "2024-12-01T10:30:00Z",
  "data": {
    "id": 1,
    "title": "Article Title",
    "content": "Article content...",
    "author": "John Doe",
    "status": "draft",
    ...
  }
}
```

**Synchronization Flow:**
1. Flask API performs CRUD operation on DB1 (PostgreSQL primary)
2. After successful DB operation, publish event to Kafka topic
3. Kafka Sync service consumes event from topic
4. Sync service replicates operation to DB2 (PostgreSQL replica)
5. Implements idempotency to handle duplicate events
6. Manual offset commit only after successful DB2 operation

## Prometheus Metrics

**Key Metrics Exposed:**
- `http_requests_total` - Total HTTP requests (by method, endpoint, status)
- `http_request_duration_seconds` - Request latency histogram
- `articles_total` - Total articles gauge (by status)
- `db_queries_total` - Database query counter
- `kafka_messages_sent_total` - Kafka messages published
- `kafka_message_send_errors_total` - Kafka publish failures

**Grafana Dashboard Panels:**
- Request rate per endpoint (req/sec)
- Latency distribution (p50, p90, p99)
- Error rate by HTTP status code
- Kafka message throughput
- Database sync lag (DB1 vs DB2)
- Service resource usage (CPU/Memory)

## Important Development Notes

**Code Patterns:**

1. **Marshmallow Validation** - All API inputs validated through schemas before processing
2. **SQLAlchemy Models** - Use Flask-SQLAlchemy ORM for database operations
3. **Error Handling** - Return consistent JSON error responses with appropriate HTTP codes
4. **Kafka Idempotency** - Check event ID/timestamp before processing to avoid duplicate syncs
5. **Circuit Breaker** - GraphQL gateway should implement retry logic with exponential backoff when calling REST API

**Testing Strategy:**
- Unit tests for models, schemas, services (pytest)
- Integration tests for full CRUD flows
- Mock Kafka producer in tests unless testing integration
- Use pytest fixtures for database setup/teardown

## Environment Variables

Key variables defined in `.env`:
- `FLASK_ENV` - Environment (development/production)
- `DB1_HOST`, `DB1_PORT`, `DB1_NAME`, `DB1_USER`, `DB1_PASSWORD` - Primary database
- `DB2_HOST`, `DB2_PORT`, `DB2_NAME`, `DB2_USER`, `DB2_PASSWORD` - Replica database
- `KAFKA_BOOTSTRAP_SERVERS` - Kafka broker address
- `KAFKA_TOPIC_ARTICLES` - Kafka topic name
- `REST_API_URL` - Flask API URL for GraphQL gateway
- `SECRET_KEY` - Flask secret key

## Troubleshooting

**Kafka connection issues:**
- Ensure Zookeeper is running before Kafka: `docker-compose logs zookeeper`
- Check Kafka broker is accessible: `docker-compose logs kafka`
- Verify topic exists: `docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092`

**Database sync lag:**
- Check Kafka consumer is running: `docker-compose logs kafka-sync`
- Verify consumer group offset: Check Prometheus metrics or Kafka consumer lag
- Review dead letter queue for failed events

**GraphQL errors:**
- Verify Flask API is accessible from GraphQL container
- Check REST client timeout settings
- Review GraphQL gateway logs: `docker-compose logs graphql-gateway`

**Prometheus not scraping metrics:**
- Verify `/metrics` endpoint is accessible: `curl http://localhost:5000/metrics`
- Check Prometheus targets: http://localhost:9090/targets
- Review Prometheus logs: `docker-compose logs prometheus`
