# Documentation de l'API

Documentation complète des endpoints REST et GraphQL.

## Table des Matières
- [REST API](#rest-api)
  - [Articles](#articles)
  - [Health](#health)
- [GraphQL API](#graphql-api)
  - [Queries](#queries)
  - [Mutations](#mutations)
- [Codes de Réponse](#codes-de-réponse)
- [Exemples](#exemples)

## REST API

Base URL: `http://localhost:5000/api/v1`

### Articles

#### Lister les Articles

```http
GET /api/v1/articles
```

**Paramètres de requête:**
- `page` (integer, optionnel): Numéro de page (défaut: 1)
- `per_page` (integer, optionnel): Articles par page (défaut: 10, max: 100)
- `status` (string, optionnel): Filtrer par statut (`draft`, `published`, `archived`)
- `category` (string, optionnel): Filtrer par catégorie
- `author` (string, optionnel): Filtrer par auteur

**Exemple de requête:**
```bash
curl "http://localhost:5000/api/v1/articles?page=1&per_page=10&status=published"
```

**Réponse (200 OK):**
```json
{
  "items": [
    {
      "id": 1,
      "title": "Introduction to REST APIs",
      "content": "Content here...",
      "author": "John Doe",
      "category": "technology",
      "tags": ["api", "rest"],
      "status": "published",
      "views_count": 150,
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:20:00Z",
      "published_at": "2024-01-15T14:20:00Z"
    }
  ],
  "page_info": {
    "current_page": 1,
    "total_pages": 5,
    "per_page": 10,
    "total_items": 50,
    "has_next": true,
    "has_prev": false
  }
}
```

---

#### Obtenir un Article

```http
GET /api/v1/articles/{id}
```

**Paramètres de chemin:**
- `id` (integer, requis): ID de l'article

**Exemple de requête:**
```bash
curl http://localhost:5000/api/v1/articles/1
```

**Réponse (200 OK):**
```json
{
  "id": 1,
  "title": "Introduction to REST APIs",
  "content": "REST APIs are...",
  "author": "John Doe",
  "category": "technology",
  "tags": ["api", "rest"],
  "status": "published",
  "views_count": 151,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T14:20:00Z",
  "published_at": "2024-01-15T14:20:00Z"
}
```

**Réponse (404 Not Found):**
```json
{
  "error": "Article not found"
}
```

---

#### Créer un Article

```http
POST /api/v1/articles
```

**Headers:**
- `Content-Type: application/json`

**Corps de la requête:**
```json
{
  "title": "My New Article",
  "content": "Article content goes here...",
  "author": "Jane Smith",
  "category": "programming",
  "tags": ["python", "flask"]
}
```

**Champs:**
- `title` (string, requis): Titre (max 200 caractères)
- `content` (string, requis): Contenu de l'article
- `author` (string, requis): Nom de l'auteur (max 100 caractères)
- `category` (string, optionnel): Catégorie (défaut: "general")
- `tags` (array, optionnel): Liste de tags

**Exemple de requête:**
```bash
curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with Flask",
    "content": "Flask is a lightweight web framework...",
    "author": "Alice Johnson",
    "category": "programming",
    "tags": ["python", "flask", "web"]
  }'
```

**Réponse (201 Created):**
```json
{
  "id": 25,
  "title": "Getting Started with Flask",
  "content": "Flask is a lightweight web framework...",
  "author": "Alice Johnson",
  "category": "programming",
  "tags": ["python", "flask", "web"],
  "status": "draft",
  "views_count": 0,
  "created_at": "2024-01-20T09:15:00Z",
  "updated_at": null,
  "published_at": null
}
```

**Réponse (400 Bad Request):**
```json
{
  "errors": {
    "title": ["Missing data for required field."],
    "content": ["Content cannot be empty or just whitespace"]
  }
}
```

---

#### Mettre à Jour un Article

```http
PUT /api/v1/articles/{id}
PATCH /api/v1/articles/{id}
```

**Paramètres de chemin:**
- `id` (integer, requis): ID de l'article

**Corps de la requête:**
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "category": "technology",
  "tags": ["api", "rest", "updated"]
}
```

**Tous les champs sont optionnels pour PATCH**

**Exemple de requête:**
```bash
curl -X PUT http://localhost:5000/api/v1/articles/25 \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started with Flask - Updated",
    "category": "web-development"
  }'
```

**Réponse (200 OK):**
```json
{
  "id": 25,
  "title": "Getting Started with Flask - Updated",
  "content": "Flask is a lightweight web framework...",
  "author": "Alice Johnson",
  "category": "web-development",
  "tags": ["python", "flask", "web"],
  "status": "draft",
  "views_count": 0,
  "created_at": "2024-01-20T09:15:00Z",
  "updated_at": "2024-01-20T10:30:00Z",
  "published_at": null
}
```

---

#### Supprimer un Article

```http
DELETE /api/v1/articles/{id}
```

**Paramètres de chemin:**
- `id` (integer, requis): ID de l'article

**Exemple de requête:**
```bash
curl -X DELETE http://localhost:5000/api/v1/articles/25
```

**Réponse (204 No Content)**

Aucun corps de réponse.

**Réponse (404 Not Found):**
```json
{
  "error": "Article not found"
}
```

---

#### Publier un Article

```http
POST /api/v1/articles/{id}/publish
```

Change le statut de l'article à "published" et définit la date de publication.

**Paramètres de chemin:**
- `id` (integer, requis): ID de l'article

**Exemple de requête:**
```bash
curl -X POST http://localhost:5000/api/v1/articles/25/publish
```

**Réponse (200 OK):**
```json
{
  "id": 25,
  "title": "Getting Started with Flask",
  "content": "Flask is a lightweight web framework...",
  "author": "Alice Johnson",
  "category": "programming",
  "tags": ["python", "flask", "web"],
  "status": "published",
  "views_count": 0,
  "created_at": "2024-01-20T09:15:00Z",
  "updated_at": "2024-01-20T11:00:00Z",
  "published_at": "2024-01-20T11:00:00Z"
}
```

---

#### Rechercher des Articles

```http
GET /api/v1/articles/search
```

**Paramètres de requête:**
- `q` (string, requis): Terme de recherche

**Recherche dans:**
- Titre de l'article
- Contenu
- Nom de l'auteur

**Exemple de requête:**
```bash
curl "http://localhost:5000/api/v1/articles/search?q=flask"
```

**Réponse (200 OK):**
```json
{
  "query": "flask",
  "count": 3,
  "results": [
    {
      "id": 25,
      "title": "Getting Started with Flask",
      "content": "Flask is a lightweight web framework...",
      "author": "Alice Johnson",
      "category": "programming",
      "tags": ["python", "flask", "web"],
      "status": "published",
      "views_count": 45,
      "created_at": "2024-01-20T09:15:00Z",
      "updated_at": "2024-01-20T11:00:00Z",
      "published_at": "2024-01-20T11:00:00Z"
    }
  ]
}
```

---

### Health

#### Health Check

```http
GET /api/v1/health
```

Vérifier l'état de l'API.

**Exemple de requête:**
```bash
curl http://localhost:5000/api/v1/health
```

**Réponse (200 OK):**
```json
{
  "status": "healthy",
  "service": "flask-api"
}
```

---

#### Métriques Prometheus

```http
GET /metrics
```

Expose les métriques au format Prometheus.

**Exemple de requête:**
```bash
curl http://localhost:5000/metrics
```

**Réponse (200 OK):**
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="articles.list_articles",method="GET",status="200"} 1250.0

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="articles.list_articles",le="0.005",method="GET"} 800.0
...
```

---

## GraphQL API

Base URL: `http://localhost:4000/graphql`

GraphQL Playground: `http://localhost:4000/graphql`

### Types

#### Article

```graphql
type Article {
  id: ID!
  title: String!
  content: String!
  author: String!
  category: String
  tags: [String!]!
  status: ArticleStatus!
  viewsCount: Int!
  createdAt: DateTime!
  updatedAt: DateTime
  publishedAt: DateTime
}
```

#### ArticleStatus

```graphql
enum ArticleStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}
```

#### ArticleConnection

```graphql
type ArticleConnection {
  items: [Article!]!
  pageInfo: PageInfo!
}
```

#### PageInfo

```graphql
type PageInfo {
  currentPage: Int!
  totalPages: Int!
  perPage: Int!
  totalItems: Int!
  hasNext: Boolean!
  hasPrev: Boolean!
}
```

### Queries

#### article

Récupère un article par son ID.

```graphql
query GetArticle {
  article(id: "1") {
    id
    title
    content
    author
    category
    tags
    status
    viewsCount
    createdAt
  }
}
```

**Réponse:**
```json
{
  "data": {
    "article": {
      "id": "1",
      "title": "Introduction to REST APIs",
      "content": "REST APIs are...",
      "author": "John Doe",
      "category": "technology",
      "tags": ["api", "rest"],
      "status": "PUBLISHED",
      "viewsCount": 150,
      "createdAt": "2024-01-15T10:30:00+00:00"
    }
  }
}
```

---

#### articles

Liste les articles avec pagination et filtres.

```graphql
query ListArticles {
  articles(
    page: 1
    perPage: 10
    filter: {
      status: PUBLISHED
      category: "technology"
    }
  ) {
    items {
      id
      title
      author
      status
      createdAt
    }
    pageInfo {
      currentPage
      totalPages
      totalItems
      hasNext
      hasPrev
    }
  }
}
```

**Réponse:**
```json
{
  "data": {
    "articles": {
      "items": [
        {
          "id": "1",
          "title": "Introduction to REST APIs",
          "author": "John Doe",
          "status": "PUBLISHED",
          "createdAt": "2024-01-15T10:30:00+00:00"
        }
      ],
      "pageInfo": {
        "currentPage": 1,
        "totalPages": 5,
        "totalItems": 50,
        "hasNext": true,
        "hasPrev": false
      }
    }
  }
}
```

---

#### searchArticles

Recherche d'articles par terme de recherche.

```graphql
query SearchArticles {
  searchArticles(query: "flask") {
    id
    title
    author
    category
  }
}
```

---

### Mutations

#### createArticle

Crée un nouvel article.

```graphql
mutation CreateArticle {
  createArticle(input: {
    title: "GraphQL Tutorial"
    content: "GraphQL is a query language..."
    author: "Jane Smith"
    category: "programming"
    tags: ["graphql", "api"]
  }) {
    id
    title
    status
    createdAt
  }
}
```

**Réponse:**
```json
{
  "data": {
    "createArticle": {
      "id": "26",
      "title": "GraphQL Tutorial",
      "status": "DRAFT",
      "createdAt": "2024-01-20T12:00:00+00:00"
    }
  }
}
```

---

#### updateArticle

Met à jour un article existant.

```graphql
mutation UpdateArticle {
  updateArticle(
    id: "26"
    input: {
      title: "GraphQL Tutorial - Updated"
      category: "web-development"
    }
  ) {
    id
    title
    category
    updatedAt
  }
}
```

---

#### deleteArticle

Supprime un article.

```graphql
mutation DeleteArticle {
  deleteArticle(id: "26")
}
```

**Réponse:**
```json
{
  "data": {
    "deleteArticle": true
  }
}
```

---

#### publishArticle

Publie un article.

```graphql
mutation PublishArticle {
  publishArticle(id: "26") {
    id
    status
    publishedAt
  }
}
```

**Réponse:**
```json
{
  "data": {
    "publishArticle": {
      "id": "26",
      "status": "PUBLISHED",
      "publishedAt": "2024-01-20T13:00:00+00:00"
    }
  }
}
```

---

## Codes de Réponse

### Codes de Succès

| Code | Description |
|------|-------------|
| 200 | OK - La requête a réussi |
| 201 | Created - L'article a été créé |
| 204 | No Content - L'article a été supprimé |

### Codes d'Erreur

| Code | Description |
|------|-------------|
| 400 | Bad Request - Données invalides |
| 404 | Not Found - Article non trouvé |
| 500 | Internal Server Error - Erreur serveur |

---

## Exemples

### Exemple 1: Créer et Publier un Article (REST)

```bash
# 1. Créer l'article
response=$(curl -X POST http://localhost:5000/api/v1/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mon Article",
    "content": "Contenu de mon article",
    "author": "Moi",
    "category": "test"
  }')

# Extraire l'ID
article_id=$(echo $response | jq -r '.id')

# 2. Publier l'article
curl -X POST "http://localhost:5000/api/v1/articles/$article_id/publish"
```

### Exemple 2: Workflow Complet avec GraphQL

```graphql
# 1. Créer un article
mutation {
  createArticle(input: {
    title: "Test Article"
    content: "Test content"
    author: "Test Author"
  }) {
    id
  }
}

# 2. Mettre à jour l'article
mutation {
  updateArticle(id: "1", input: {
    title: "Updated Title"
  }) {
    id
    title
  }
}

# 3. Publier l'article
mutation {
  publishArticle(id: "1") {
    id
    status
  }
}

# 4. Récupérer l'article
query {
  article(id: "1") {
    id
    title
    status
    publishedAt
  }
}
```

### Exemple 3: Pagination avec GraphQL

```graphql
# Page 1
query {
  page1: articles(page: 1, perPage: 5) {
    items { id title }
    pageInfo { currentPage hasNext }
  }
}

# Page 2
query {
  page2: articles(page: 2, perPage: 5) {
    items { id title }
    pageInfo { currentPage hasPrev hasNext }
  }
}
```

---

Pour plus d'informations, consultez:
- [README.md](../README.md)
- [Guide d'Installation](INSTALLATION.md)
- GraphQL Playground: http://localhost:4000/graphql
