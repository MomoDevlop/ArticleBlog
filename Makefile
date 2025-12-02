.PHONY: help build up down logs restart clean test seed health

help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

build: ## Build all Docker images
	docker-compose build

up: ## Start all services
	docker-compose up -d
	@echo "Services are starting..."
	@echo "Flask API: http://localhost:5000"
	@echo "GraphQL Gateway: http://localhost:4000/graphql"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000 (admin/admin)"

down: ## Stop all services
	docker-compose down

down-volumes: ## Stop all services and remove volumes
	docker-compose down -v

logs: ## View logs from all services
	docker-compose logs -f

logs-api: ## View Flask API logs
	docker-compose logs -f flask-api

logs-graphql: ## View GraphQL Gateway logs
	docker-compose logs -f graphql-gateway

logs-kafka: ## View Kafka logs
	docker-compose logs -f kafka

logs-sync: ## View Kafka Sync service logs
	docker-compose logs -f kafka-sync

restart: ## Restart all services
	docker-compose restart

restart-api: ## Restart Flask API
	docker-compose restart flask-api

restart-graphql: ## Restart GraphQL Gateway
	docker-compose restart graphql-gateway

clean: ## Stop services and remove containers, volumes, and images
	docker-compose down -v --rmi all
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

test: ## Run tests
	docker-compose exec flask-api pytest -v

test-coverage: ## Run tests with coverage
	docker-compose exec flask-api pytest --cov=app --cov-report=html --cov-report=term

test-graphql: ## Run GraphQL tests
	docker-compose exec graphql-gateway pytest -v

seed: ## Seed database with test data
	docker-compose exec flask-api python /app/scripts/seed_data.py

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:5000/api/v1/health || echo "Flask API: DOWN"
	@curl -s http://localhost:4000/health || echo "GraphQL Gateway: DOWN"
	@curl -s http://localhost:9090/-/healthy || echo "Prometheus: DOWN"
	@curl -s http://localhost:3000/api/health || echo "Grafana: DOWN"

ps: ## Show running containers
	docker-compose ps

db-migrate: ## Run database migrations
	docker-compose exec flask-api flask db migrate

db-upgrade: ## Upgrade database to latest migration
	docker-compose exec flask-api flask db upgrade

db1-shell: ## Connect to PostgreSQL DB1
	docker-compose exec postgres-db1 psql -U blog_user -d blog_db

db2-shell: ## Connect to PostgreSQL DB2
	docker-compose exec postgres-db2 psql -U blog_user -d blog_replica_db

kafka-topics: ## List Kafka topics
	docker-compose exec kafka kafka-topics --list --bootstrap-server localhost:9092

kafka-consume: ## Consume Kafka messages (article-events topic)
	docker-compose exec kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic article-events --from-beginning
