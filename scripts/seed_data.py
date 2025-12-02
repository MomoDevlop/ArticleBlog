#!/usr/bin/env python3
"""
Seed script to populate database with test data
"""

import requests
import json
from faker import Faker
import random
import time

fake = Faker()

API_BASE_URL = "http://localhost:5000/api/v1"

# Categories for articles
CATEGORIES = ['technology', 'science', 'programming', 'architecture', 'design', 'business']

# Tags pool
TAGS_POOL = [
    'python', 'javascript', 'api', 'rest', 'graphql', 'microservices',
    'docker', 'kubernetes', 'aws', 'cloud', 'database', 'postgresql',
    'mongodb', 'react', 'vue', 'angular', 'nodejs', 'flask', 'django',
    'machine-learning', 'ai', 'data-science', 'devops', 'cicd'
]


def create_article(title, content, author, category, tags, publish=False):
    """Create an article via API"""
    data = {
        "title": title,
        "content": content,
        "author": author,
        "category": category,
        "tags": tags
    }

    try:
        response = requests.post(f"{API_BASE_URL}/articles", json=data)
        response.raise_for_status()
        article = response.json()

        print(f"✓ Created article: {article['id']} - {title}")

        # Publish if requested
        if publish and random.random() > 0.3:  # 70% chance to publish
            publish_response = requests.post(f"{API_BASE_URL}/articles/{article['id']}/publish")
            if publish_response.status_code == 200:
                print(f"  → Published article {article['id']}")

        return article

    except requests.exceptions.RequestException as e:
        print(f"✗ Error creating article: {str(e)}")
        return None


def main():
    """Main seeding function"""
    print("=" * 60)
    print("Blog API Data Seeding")
    print("=" * 60)
    print()

    # Check if API is accessible
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        response.raise_for_status()
        print("✓ API is accessible")
    except requests.exceptions.RequestException as e:
        print(f"✗ API is not accessible: {str(e)}")
        print("  Make sure the Flask API is running (docker-compose up)")
        return

    print()
    print("Creating articles...")
    print("-" * 60)

    # Sample article templates
    articles_data = [
        {
            "title": "Introduction to RESTful API Design",
            "content": "RESTful APIs are the backbone of modern web applications. In this article, we'll explore the fundamental principles of REST architecture, including statelessness, resource-based URLs, and HTTP methods. We'll also discuss best practices for designing scalable and maintainable APIs that follow REST conventions.",
            "author": "Sarah Johnson",
            "category": "technology",
            "tags": ["api", "rest", "web-development"],
            "publish": True
        },
        {
            "title": "GraphQL vs REST: Choosing the Right API Architecture",
            "content": "When building modern applications, choosing between GraphQL and REST can be challenging. This article compares both approaches, discussing their strengths, weaknesses, and ideal use cases. We'll examine query flexibility, performance considerations, and developer experience to help you make an informed decision.",
            "author": "Michael Chen",
            "category": "technology",
            "tags": ["graphql", "rest", "api"],
            "publish": True
        },
        {
            "title": "Microservices Architecture Patterns",
            "content": "Microservices have revolutionized how we build scalable applications. This comprehensive guide covers essential patterns including service discovery, API gateways, circuit breakers, and event-driven architecture. Learn how to decompose monolithic applications and design resilient distributed systems.",
            "author": "David Martinez",
            "category": "architecture",
            "tags": ["microservices", "architecture", "distributed-systems"],
            "publish": True
        },
        {
            "title": "Getting Started with Docker for Python Developers",
            "content": "Docker has become an essential tool for modern Python development. This tutorial guides you through containerizing Python applications, creating efficient Dockerfiles, managing dependencies, and orchestrating multi-container applications with Docker Compose. Perfect for beginners looking to streamline their development workflow.",
            "author": "Emily Watson",
            "category": "programming",
            "tags": ["docker", "python", "devops"],
            "publish": False
        },
        {
            "title": "Building Real-time Applications with Kafka",
            "content": "Apache Kafka enables building real-time streaming applications at scale. This article explores Kafka's architecture, including topics, partitions, and consumer groups. We'll implement a practical example showing how to process millions of events per second with fault tolerance and exactly-once semantics.",
            "author": "Robert Lee",
            "category": "technology",
            "tags": ["kafka", "streaming", "real-time"],
            "publish": True
        }
    ]

    # Create predefined articles
    for article_data in articles_data:
        create_article(
            title=article_data["title"],
            content=article_data["content"],
            author=article_data["author"],
            category=article_data["category"],
            tags=article_data["tags"],
            publish=article_data["publish"]
        )
        time.sleep(0.5)  # Small delay to avoid overwhelming the API

    # Create additional random articles
    print()
    print("Creating random articles...")
    print("-" * 60)

    for i in range(15):
        title = fake.sentence(nb_words=6).rstrip('.')
        content = " ".join(fake.paragraphs(nb=3))
        author = fake.name()
        category = random.choice(CATEGORIES)
        tags = random.sample(TAGS_POOL, k=random.randint(2, 5))

        create_article(
            title=title,
            content=content,
            author=author,
            category=category,
            tags=tags,
            publish=True
        )
        time.sleep(0.3)

    print()
    print("=" * 60)
    print("Seeding Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  Total articles created: {len(articles_data) + 15}")
    print()
    print("You can now:")
    print("  - View articles: http://localhost:5000/api/v1/articles")
    print("  - Query with GraphQL: http://localhost:4000/graphql")
    print("  - Monitor metrics: http://localhost:9090")
    print()


if __name__ == "__main__":
    main()
