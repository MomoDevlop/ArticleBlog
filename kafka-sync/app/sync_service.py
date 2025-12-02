import logging
import hashlib
from typing import Dict
from app.db_connector import DB2Connector

logger = logging.getLogger(__name__)


class SyncService:
    """Service for synchronizing articles from DB1 to DB2 via Kafka events"""

    def __init__(self, db_connector: DB2Connector):
        """
        Initialize sync service

        Args:
            db_connector: DB2 database connector
        """
        self.db = db_connector

    def _generate_event_id(self, event_type: str, article_id: int, timestamp: str) -> str:
        """
        Generate unique event ID for idempotency

        Args:
            event_type: Type of event
            article_id: Article ID
            timestamp: Event timestamp

        Returns:
            Unique event ID
        """
        key = f"{event_type}:{article_id}:{timestamp}"
        return hashlib.md5(key.encode()).hexdigest()

    def handle_event(self, event: Dict) -> bool:
        """
        Handle a Kafka event

        Args:
            event: Event data

        Returns:
            True if successful, False otherwise
        """
        event_type = event.get('event_type')
        timestamp = event.get('timestamp')
        data = event.get('data', {})

        if not event_type or not data:
            logger.error(f"Invalid event format: {event}")
            return False

        article_id = data.get('id')
        if not article_id:
            logger.error(f"Article ID missing in event: {event}")
            return False

        # Generate event ID for idempotency
        event_id = self._generate_event_id(event_type, article_id, timestamp)

        # Check if event already processed
        if self.db.is_event_processed(event_id):
            logger.info(f"Event {event_id} already processed, skipping")
            return True

        # Route to appropriate handler
        success = False
        if event_type == 'article.created':
            success = self.handle_created(data)
        elif event_type == 'article.updated':
            success = self.handle_updated(data)
        elif event_type == 'article.deleted':
            success = self.handle_deleted(data)
        elif event_type == 'article.published':
            success = self.handle_published(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return False

        # Mark event as processed if successful
        if success:
            self.db.mark_event_processed(event_id, event_type, article_id, event)
            logger.info(f"Successfully processed event: {event_type} for article {article_id}")
        else:
            logger.error(f"Failed to process event: {event_type} for article {article_id}")

        return success

    def handle_created(self, data: Dict) -> bool:
        """
        Handle article.created event

        Args:
            data: Article data

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Handling article.created: ID={data.get('id')}")
        return self.db.insert_article(data)

    def handle_updated(self, data: Dict) -> bool:
        """
        Handle article.updated event

        Args:
            data: Article data

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Handling article.updated: ID={data.get('id')}")
        article_id = data.get('id')
        return self.db.update_article(article_id, data)

    def handle_deleted(self, data: Dict) -> bool:
        """
        Handle article.deleted event

        Args:
            data: Article data

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Handling article.deleted: ID={data.get('id')}")
        article_id = data.get('id')
        return self.db.delete_article(article_id)

    def handle_published(self, data: Dict) -> bool:
        """
        Handle article.published event (same as update)

        Args:
            data: Article data

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Handling article.published: ID={data.get('id')}")
        article_id = data.get('id')
        return self.db.update_article(article_id, data)
