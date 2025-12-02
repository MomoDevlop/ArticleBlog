import json
import logging
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time

logger = logging.getLogger(__name__)


class KafkaProducerService:
    """Service for publishing events to Kafka"""

    def __init__(self, bootstrap_servers, topic):
        """
        Initialize Kafka producer

        Args:
            bootstrap_servers (str): Kafka bootstrap servers
            topic (str): Kafka topic name
        """
        self.topic = topic
        self.producer = None
        self.enabled = True

        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Kafka producer initialized successfully for topic: {topic}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {str(e)}")
            self.enabled = False

    def publish_event(self, event_type, article_data, max_retries=3):
        """
        Publish an event to Kafka

        Args:
            event_type (str): Type of event (article.created, article.updated, etc.)
            article_data (dict): Article data
            max_retries (int): Maximum number of retry attempts

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.enabled or not self.producer:
            logger.warning("Kafka producer is disabled or not initialized")
            return False

        event = {
            'event_type': event_type,
            'timestamp': datetime.utcnow().isoformat(),
            'data': article_data
        }

        for attempt in range(max_retries):
            try:
                # Send message
                future = self.producer.send(self.topic, value=event)

                # Wait for message to be sent (with timeout)
                record_metadata = future.get(timeout=10)

                logger.info(
                    f"Event published successfully: {event_type} "
                    f"(topic: {record_metadata.topic}, partition: {record_metadata.partition}, "
                    f"offset: {record_metadata.offset})"
                )
                return True

            except KafkaError as e:
                logger.error(f"Kafka error on attempt {attempt + 1}/{max_retries}: {str(e)}")
                if attempt < max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed to publish event after {max_retries} attempts")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error publishing event: {str(e)}")
                return False

        return False

    def publish_article_created(self, article_data):
        """Publish article.created event"""
        return self.publish_event('article.created', article_data)

    def publish_article_updated(self, article_data):
        """Publish article.updated event"""
        return self.publish_event('article.updated', article_data)

    def publish_article_deleted(self, article_data):
        """Publish article.deleted event"""
        return self.publish_event('article.deleted', article_data)

    def publish_article_published(self, article_data):
        """Publish article.published event"""
        return self.publish_event('article.published', article_data)

    def close(self):
        """Close the Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
