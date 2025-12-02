import os
import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import config
from app.models.article import db
from app.routes import articles_bp
from app.services.kafka_producer import KafkaProducerService
from app.services.article_service import ArticleService
from app.utils.metrics import init_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app(config_name=None):
    """
    Application factory pattern

    Args:
        config_name (str): Configuration name (development, production, testing)

    Returns:
        Flask: Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app.config.from_object(config[config_name])
    logger.info(f"Loaded configuration: {config_name}")

    # Initialize extensions
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    Migrate(app, db)

    # Initialize Kafka producer
    kafka_producer = None
    if app.config.get('KAFKA_ENABLED', True):
        try:
            kafka_producer = KafkaProducerService(
                bootstrap_servers=app.config['KAFKA_BOOTSTRAP_SERVERS'],
                topic=app.config['KAFKA_TOPIC_ARTICLES']
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")

    # Initialize services
    article_service = ArticleService(kafka_producer=kafka_producer)
    app.article_service = article_service

    # Register blueprints
    app.register_blueprint(articles_bp)
    logger.info("Blueprints registered")

    # Initialize Prometheus metrics
    init_metrics(app)
    logger.info("Prometheus metrics initialized")

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")

    @app.route('/')
    def index():
        """Root endpoint"""
        return {
            'service': 'Blog API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/v1/health',
                'articles': '/api/v1/articles',
                'metrics': '/metrics',
                'docs': '/docs'
            }
        }

    logger.info("Flask application created successfully")
    return app
