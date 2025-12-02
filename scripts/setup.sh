#!/bin/bash

# Blog API Setup Script
# This script sets up the entire project environment

set -e  # Exit on error

echo "=========================================="
echo "Blog API Project Setup"
echo "=========================================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker found: $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose from https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✓ Docker Compose found: $(docker-compose --version)"

echo ""
echo "=========================================="
echo "Environment Configuration"
echo "=========================================="

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please review and update .env file with your configuration"
    echo "   Especially update passwords and secret keys!"
else
    echo "✓ .env file already exists"
fi

echo ""
echo "=========================================="
echo "Building Docker Images"
echo "=========================================="
docker-compose build

echo ""
echo "=========================================="
echo "Starting Services"
echo "=========================================="
docker-compose up -d

echo ""
echo "Waiting for services to be ready..."
sleep 30

echo ""
echo "=========================================="
echo "Running Database Migrations"
echo "=========================================="
docker-compose exec -T flask-api flask db upgrade || echo "⚠️  Migrations not yet configured"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Services are running:"
echo "  - Flask API:        http://localhost:5000"
echo "  - GraphQL Gateway:  http://localhost:4000/graphql"
echo "  - Prometheus:       http://localhost:9090"
echo "  - Grafana:          http://localhost:3000 (admin/admin)"
echo ""
echo "Next steps:"
echo "  1. Check service health: make health"
echo "  2. Seed test data:      make seed"
echo "  3. View logs:           make logs"
echo ""
echo "For more commands, run: make help"
echo "=========================================="
