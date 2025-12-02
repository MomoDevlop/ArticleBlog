#!/bin/bash

# Health Check Script for all services

echo "=========================================="
echo "Blog API System Health Check"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    echo -n "Checking $name... "

    response=$(curl -s -o /dev/null -w "%{http_code}" $url 2>/dev/null)

    if [ "$response" == "$expected_code" ]; then
        echo -e "${GREEN}✓ OK${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response)"
        return 1
    fi
}

check_docker_service() {
    local service_name=$1

    echo -n "Checking Docker service $service_name... "

    if docker-compose ps | grep -q "$service_name.*Up"; then
        echo -e "${GREEN}✓ Running${NC}"
        return 0
    else
        echo -e "${RED}✗ Not Running${NC}"
        return 1
    fi
}

total_checks=0
passed_checks=0

# Check Docker services
echo "Docker Services:"
echo "----------------"

for service in postgres-db1 postgres-db2 zookeeper kafka flask-api graphql-gateway kafka-sync prometheus grafana; do
    check_docker_service $service
    total_checks=$((total_checks + 1))
    if [ $? -eq 0 ]; then
        passed_checks=$((passed_checks + 1))
    fi
done

echo ""
echo "HTTP Endpoints:"
echo "---------------"

# Check HTTP endpoints
check_service "Flask API Health" "http://localhost:5000/api/v1/health" 200
total_checks=$((total_checks + 1))
if [ $? -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
fi

check_service "Flask API Metrics" "http://localhost:5000/metrics" 200
total_checks=$((total_checks + 1))
if [ $? -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
fi

check_service "GraphQL Gateway Health" "http://localhost:4000/health" 200
total_checks=$((total_checks + 1))
if [ $? -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
fi

check_service "GraphQL Endpoint" "http://localhost:4000/graphql" 200
total_checks=$((total_checks + 1))
if [ $? -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
fi

check_service "Prometheus" "http://localhost:9090/-/healthy" 200
total_checks=$((total_checks + 1))
if [ $? -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
fi

check_service "Grafana" "http://localhost:3000/api/health" 200
total_checks=$((total_checks + 1))
if [ $? -eq 0 ]; then
    passed_checks=$((passed_checks + 1))
fi

echo ""
echo "=========================================="
echo "Health Check Summary"
echo "=========================================="
echo ""

percentage=$((passed_checks * 100 / total_checks))

if [ $percentage -eq 100 ]; then
    echo -e "${GREEN}All checks passed!${NC} ($passed_checks/$total_checks)"
    exit 0
elif [ $percentage -ge 70 ]; then
    echo -e "${YELLOW}Most checks passed${NC} ($passed_checks/$total_checks - $percentage%)"
    exit 0
else
    echo -e "${RED}Health check failed${NC} ($passed_checks/$total_checks - $percentage%)"
    echo ""
    echo "Try:"
    echo "  - docker-compose logs [service-name]"
    echo "  - docker-compose restart [service-name]"
    exit 1
fi
