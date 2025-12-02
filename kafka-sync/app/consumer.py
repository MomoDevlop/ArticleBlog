import json
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import time
from app.sync_service import SyncService

logger = logging.getLogger(__name__)


class ArticleEventConsumer:
    """Kafka consumer for article events"""

    def __init__(
        self,
        bootstrap_servers: str,
        topic: str,
        group_id: str,
        sync_service: SyncService
    ):
        """
        Initialize Kafka consumer

        Args:
            bootstrap_servers: Kafka bootstrap servers
            topic: Kafka topic to subscribe to
            group_id: Consumer group ID
            sync_service: Sync service instance
        """
        self.topic = topic
        self.group_id = group_id
        self.sync_service = sync_service
        self.consumer = None
        self.running = False

        # Initialize consumer with retry logic
        self._init_consumer(bootstrap_servers)

    def _init_consumer(self, bootstrap_servers: str, max_retries: int = 5):
        """
        Initialize Kafka consumer with retry logic

        Args:
            bootstrap_servers: Kafka bootstrap servers
            max_retries: Maximum retry attempts
        """
        for attempt in range(max_retries):
            try:
                self.consumer = KafkaConsumer(
                    self.topic,
                    bootstrap_servers=bootstrap_servers.split(','),
                    group_id=self.group_id,
                    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                    enable_auto_commit=False,  # Manual commit for reliability
                    auto_offset_reset='earliest',
                    max_poll_records=10,
                    session_timeout_ms=30000,
                    heartbeat_interval_ms=10000
                )

                logger.info(f"Kafka consumer initialized successfully")
                logger.info(f"  Topic: {self.topic}")
                logger.info(f"  Group ID: {self.group_id}")
                logger.info(f"  Bootstrap servers: {bootstrap_servers}")
                return

            except Exception as e:
                wait_time = 2 ** attempt
                logger.error(f"Failed to initialize Kafka consumer (attempt {attempt + 1}/{max_retries}): {str(e)}")

                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to initialize Kafka consumer after {max_retries} attempts")

    def start(self):
        """Start consuming messages from Kafka"""
        if not self.consumer:
            logger.error("Consumer not initialized")
            return

        self.running = True
        logger.info(f"Starting to consume messages from topic: {self.topic}")

        try:
            for message in self.consumer:
                if not self.running:
                    logger.info("Consumer stopped")
                    break

                try:
                    # Get event from message
                    event = message.value

                    logger.info(
                        f"Received message: topic={message.topic}, "
                        f"partition={message.partition}, offset={message.offset}, "
                        f"event_type={event.get('event_type')}"
                    )

                    # Process event
                    success = self.sync_service.handle_event(event)

                    if success:
                        # Commit offset only if processing was successful
                        self.consumer.commit()
                        logger.debug(f"Committed offset: {message.offset}")
                    else:
                        logger.error(f"Failed to process event, not committing offset: {message.offset}")
                        # In production, you might want to:
                        # 1. Add to dead letter queue
                        # 2. Implement retry with backoff
                        # 3. Skip after N attempts
                        # For now, we commit to avoid getting stuck
                        time.sleep(5)
                        self.consumer.commit()
                        logger.warning(f"Committed offset despite failure to avoid blocking: {message.offset}")

                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {str(e)}")
                    # Skip malformed messages
                    self.consumer.commit()

                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}", exc_info=True)
                    # Commit to avoid getting stuck on same message
                    time.sleep(5)
                    self.consumer.commit()

        except KafkaError as e:
            logger.error(f"Kafka error: {str(e)}")
            raise

        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")

        finally:
            self.stop()

    def stop(self):
        """Stop the consumer"""
        self.running = False

        if self.consumer:
            try:
                self.consumer.close()
                logger.info("Kafka consumer closed")
            except Exception as e:
                logger.error(f"Error closing consumer: {str(e)}")
