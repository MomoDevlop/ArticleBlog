import os
import logging
import signal
import sys
from app.db_connector import DB2Connector
from app.sync_service import SyncService
from app.consumer import ArticleEventConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global consumer instance for signal handling
consumer_instance = None


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if consumer_instance:
        consumer_instance.stop()
    sys.exit(0)


def main():
    """Main entry point"""
    global consumer_instance

    # Get configuration from environment
    kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC_ARTICLES', 'article-events')
    kafka_group_id = os.getenv('KAFKA_GROUP_ID', 'blog-sync-group')
    db2_url = os.getenv('DB2_URL', 'postgresql://blog_user:blog_password@postgres-db2:5432/blog_replica_db')

    logger.info("=" * 60)
    logger.info("Kafka Sync Service Starting")
    logger.info("=" * 60)
    logger.info(f"Kafka Servers: {kafka_bootstrap_servers}")
    logger.info(f"Kafka Topic: {kafka_topic}")
    logger.info(f"Kafka Group ID: {kafka_group_id}")
    logger.info(f"DB2 URL: {db2_url.split('@')[1] if '@' in db2_url else db2_url}")
    logger.info("=" * 60)

    try:
        # Initialize DB2 connector
        logger.info("Initializing DB2 connector...")
        db_connector = DB2Connector(db2_url)

        # Check DB2 health
        if not db_connector.health_check():
            logger.error("DB2 health check failed")
            sys.exit(1)

        logger.info("DB2 connection established successfully")

        # Initialize sync service
        logger.info("Initializing sync service...")
        sync_service = SyncService(db_connector)

        # Initialize and start consumer
        logger.info("Initializing Kafka consumer...")
        consumer_instance = ArticleEventConsumer(
            bootstrap_servers=kafka_bootstrap_servers,
            topic=kafka_topic,
            group_id=kafka_group_id,
            sync_service=sync_service
        )

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("=" * 60)
        logger.info("Kafka Sync Service Started Successfully")
        logger.info("Listening for events...")
        logger.info("=" * 60)

        # Start consuming
        consumer_instance.start()

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
