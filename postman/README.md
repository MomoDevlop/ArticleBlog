# Collection Postman - Blog API

Cette collection Postman contient **40+ cas de test** pour tester tous les endpoints de l'API Blog (REST + GraphQL).

## Fichiers

- **Blog-API-Collection.postman_collection.json** - Collection principale avec tous les tests
- **Blog-API-Local.postman_environment.json** - Environnement local (localhost)

## Installation

### 1. Importer la Collection

**Option A : Via l'interface Postman**
1. Ouvrez Postman
2. Cliquez sur **Import** (en haut à gauche)
3. Glissez-déposez le fichier `Blog-API-Collection.postman_collection.json`
4. Cliquez sur **Import**

**Option B : Via le bouton Import**
1. Cliquez sur **Collections** dans la barre latérale
2. Cliquez sur **Import**
3. Sélectionnez `Blog-API-Collection.postman_collection.json`

### 2. Importer l'Environnement

1. Cliquez sur **Environments** dans la barre latérale
2. Cliquez sur **Import**
3. Sélectionnez `Blog-API-Local.postman_environment.json`
4. Sélectionnez l'environnement **"Blog API - Local Environment"** dans le menu déroulant (en haut à droite)

## Structure de la Collection

La collection est organisée en **6 dossiers** :

### 1. Health & Metrics (3 tests)
- ✅ Health Check - Flask API
- ✅ Health Check - GraphQL Gateway
- ✅ Prometheus Metrics

### 2. Articles - CRUD Operations (7 tests)
- ✅ List All Articles
- ✅ List Articles - With Pagination
- ✅ Get Single Article
- ✅ Create Article
- ✅ Update Article (PUT)
- ✅ Partial Update Article (PATCH)
- ✅ Delete Article

### 3. Articles - Advanced Features (7 tests)
- ✅ Filter by Status - Published
- ✅ Filter by Status - Draft
- ✅ Filter by Category
- ✅ Filter by Author
- ✅ Search Articles - GraphQL
- ✅ Search Articles - Flask
- ✅ Publish Article

### 4. GraphQL - Queries (5 tests)
- ✅ Query - Get All Articles
- ✅ Query - Get Single Article
- ✅ Query - Filter by Status
- ✅ Query - Filter by Category
- ✅ Query - Search Articles

### 5. GraphQL - Mutations (4 tests)
- ✅ Mutation - Create Article
- ✅ Mutation - Update Article
- ✅ Mutation - Publish Article
- ✅ Mutation - Delete Article

### 6. Error Cases & Validation (6 tests)
- ✅ Get Non-Existent Article (404)
- ✅ Create Article - Missing Required Fields
- ✅ Update Non-Existent Article (404)
- ✅ Delete Non-Existent Article (404)
- ✅ Search Without Query Parameter
- ✅ GraphQL - Invalid Query Syntax

## Exécuter les Tests

### Exécuter toute la collection

1. Cliquez sur **Blog API - REST & GraphQL** (nom de la collection)
2. Cliquez sur **Run** (bouton bleu)
3. Sélectionnez tous les dossiers/requêtes que vous voulez exécuter
4. Cliquez sur **Run Blog API - REST & GraphQL**
5. Observez les résultats des tests en temps réel

### Exécuter un dossier spécifique

1. Cliquez sur le dossier (ex: "2. Articles - CRUD Operations")
2. Cliquez sur **Run**
3. Les tests de ce dossier uniquement seront exécutés

### Exécuter une requête individuelle

1. Cliquez sur la requête
2. Cliquez sur **Send**
3. Vérifiez la réponse et les résultats des tests dans l'onglet **Test Results**

## Tests Automatiques

Chaque requête inclut des **tests automatiques** qui vérifient :

✅ **Code de statut HTTP** (200, 201, 204, 400, 404)
✅ **Structure de la réponse** (présence des champs requis)
✅ **Validation des données** (types, valeurs)
✅ **Logique métier** (incrémentation des vues, changement de statut)

### Exemple de tests

```javascript
// Test 1 : Vérifier le code de statut
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// Test 2 : Vérifier la structure de la réponse
pm.test("Response has items and page_info", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('items');
    pm.expect(jsonData).to.have.property('page_info');
});

// Test 3 : Sauvegarder l'ID pour les tests suivants
pm.collectionVariables.set('created_article_id', jsonData.id);
```

## Variables de Collection

La collection utilise des **variables dynamiques** pour chaîner les tests :

| Variable | Description | Usage |
|----------|-------------|-------|
| `created_article_id` | ID de l'article créé via REST | Utilisé pour UPDATE, DELETE |
| `graphql_article_id` | ID de l'article créé via GraphQL | Utilisé pour les mutations GraphQL |

Ces variables sont automatiquement remplies lors de l'exécution des tests de création.

## Variables d'Environnement

L'environnement **Blog API - Local** définit :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `REST_API_URL` | `http://localhost:5000/api/v1` | URL de l'API Flask |
| `GRAPHQL_URL` | `http://localhost:4000` | URL du Gateway GraphQL |
| `PROMETHEUS_URL` | `http://localhost:9090` | URL de Prometheus |
| `GRAFANA_URL` | `http://localhost:3000` | URL de Grafana |

### Créer un environnement de production

1. Dupliquez l'environnement **Local**
2. Renommez-le en **"Blog API - Production"**
3. Modifiez les URLs :
   ```
   REST_API_URL: https://api.votredomaine.com/api/v1
   GRAPHQL_URL: https://graphql.votredomaine.com
   ```

## Ordre d'Exécution Recommandé

Pour tester le workflow complet, exécutez dans cet ordre :

1. **Health & Metrics** - Vérifier que les services sont opérationnels
2. **Articles - CRUD Operations** - Tester les opérations de base
3. **Articles - Advanced Features** - Tester les fonctionnalités avancées
4. **GraphQL - Queries** - Tester les requêtes GraphQL
5. **GraphQL - Mutations** - Tester les mutations GraphQL
6. **Error Cases & Validation** - Tester la gestion d'erreurs

## Cas de Test par Endpoint

### REST API (13 endpoints)

| Méthode | Endpoint | Test | Status |
|---------|----------|------|--------|
| GET | `/health` | Vérifier santé du service | ✅ 200 |
| GET | `/metrics` | Récupérer métriques Prometheus | ✅ 200 |
| GET | `/articles` | Liste avec pagination | ✅ 200 |
| GET | `/articles?page=2&per_page=2` | Pagination personnalisée | ✅ 200 |
| GET | `/articles/1` | Article spécifique | ✅ 200 |
| POST | `/articles` | Créer article | ✅ 201 |
| PUT | `/articles/{id}` | Mise à jour complète | ✅ 200 |
| PATCH | `/articles/{id}` | Mise à jour partielle | ✅ 200 |
| DELETE | `/articles/{id}` | Supprimer article | ✅ 204 |
| GET | `/articles?status=published` | Filtrer par statut | ✅ 200 |
| GET | `/articles?category=technology` | Filtrer par catégorie | ✅ 200 |
| GET | `/articles/search?q=graphql` | Rechercher articles | ✅ 200 |
| POST | `/articles/{id}/publish` | Publier article | ✅ 200 |

### GraphQL (9 opérations)

| Type | Opération | Test | Status |
|------|-----------|------|--------|
| Query | `articles` | Liste paginée | ✅ 200 |
| Query | `article(id)` | Article spécifique | ✅ 200 |
| Query | `articles(filter)` | Filtrer par statut | ✅ 200 |
| Query | `articles(filter)` | Filtrer par catégorie | ✅ 200 |
| Query | `searchArticles(query)` | Recherche | ✅ 200 |
| Mutation | `createArticle` | Créer article | ✅ 200 |
| Mutation | `updateArticle` | Modifier article | ✅ 200 |
| Mutation | `publishArticle` | Publier article | ✅ 200 |
| Mutation | `deleteArticle` | Supprimer article | ✅ 200 |

### Cas d'Erreur (6 tests)

| Test | Status Attendu | Validé |
|------|---------------|--------|
| Article inexistant (GET) | 404 | ✅ |
| Article inexistant (UPDATE) | 404 | ✅ |
| Article inexistant (DELETE) | 404 | ✅ |
| Création sans champs requis | 400 | ✅ |
| Recherche sans paramètre | 400 | ✅ |
| GraphQL syntaxe invalide | 400 | ✅ |

## Conseils

### 1. Exécuter en mode Collection Runner

Pour obtenir un rapport détaillé :
1. Cliquez sur **Runner** dans Postman
2. Glissez-déposez la collection
3. Sélectionnez l'environnement **Local**
4. Configurez le délai entre requêtes (500ms recommandé)
5. Cliquez sur **Run**

### 2. Exporter les résultats

Après avoir exécuté la collection :
1. Cliquez sur **Export Results**
2. Choisissez le format JSON ou HTML
3. Incluez le rapport dans votre documentation

### 3. Tests en ligne de commande (Newman)

Installez Newman :
```bash
npm install -g newman
```

Exécutez la collection :
```bash
newman run Blog-API-Collection.postman_collection.json \
  -e Blog-API-Local.postman_environment.json \
  --reporters cli,html \
  --reporter-html-export report.html
```

### 4. Intégration CI/CD

Ajoutez dans votre pipeline :
```yaml
# .github/workflows/api-tests.yml
- name: Run Postman Tests
  run: |
    newman run postman/Blog-API-Collection.postman_collection.json \
      -e postman/Blog-API-Local.postman_environment.json \
      --bail
```

## Résolution de Problèmes

### Les tests échouent avec des erreurs de connexion

**Solution** : Vérifiez que Docker Compose est lancé :
```bash
cd blog-api-graphql-sync
docker-compose up -d
docker-compose ps  # Tous les services doivent être "Up"
```

### Variables non définies

**Solution** : Assurez-vous que l'environnement **Blog API - Local** est sélectionné dans le menu déroulant en haut à droite de Postman.

### Tests de création/suppression échouent

**Solution** : Exécutez les tests dans l'ordre. Les tests de suppression dépendent des IDs créés par les tests de création.

### Timeout sur les requêtes

**Solution** : Augmentez le timeout dans Postman :
1. Settings → General → Request timeout → 30000 ms

## Documentation Complémentaire

- [Documentation API complète](../docs/API_DOCUMENTATION.md)
- [Guide d'installation](../docs/INSTALLATION.md)
- [README principal](../README.md)

## Utilisation Académique

Cette collection est parfaite pour :
- ✅ Démontrer le fonctionnement de l'API lors d'une présentation
- ✅ Tester automatiquement avant une soumission
- ✅ Valider la synchronisation Kafka (créer un article via REST, vérifier via GraphQL)
- ✅ Générer un rapport de tests complet pour la documentation

## Support

En cas de problème :
1. Vérifiez que tous les services Docker sont UP
2. Consultez les logs : `docker-compose logs -f`
3. Relancez les services : `docker-compose restart`

---

**Bonne chance avec votre projet académique !**
