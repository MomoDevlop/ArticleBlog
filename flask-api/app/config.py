import os
from datetime import timedelta


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://blog_user:blog_password@localhost:5432/blog_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC_ARTICLES = os.getenv('KAFKA_TOPIC_ARTICLES', 'article-events')

    # Pagination
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

    # CORS
    CORS_ORIGINS = ['*']


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

    # More restrictive CORS in production
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    # Disable Kafka for tests
    KAFKA_ENABLED = False


# Config dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
