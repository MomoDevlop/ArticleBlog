import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import time

logger = logging.getLogger(__name__)

Base = declarative_base()


class Article(Base):
    """Article model for DB2"""
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(100), nullable=False)
    category = Column(String(50), default='general')
    tags = Column(JSON, default=list)
    status = Column(String(20), default='draft')
    views_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    published_at = Column(DateTime)


class ProcessedEvent(Base):
    """Table for tracking processed events (idempotency)"""
    __tablename__ = 'processed_events'

    event_id = Column(String(255), primary_key=True)
    event_type = Column(String(50), nullable=False)
    article_id = Column(Integer)
    processed_at = Column(DateTime, default=datetime.utcnow)
    event_data = Column(JSON)


class DB2Connector:
    """Database connector for PostgreSQL DB2"""

    def __init__(self, db_url: str, pool_size: int = 10):
        """
        Initialize DB2 connector

        Args:
            db_url: Database connection URL
            pool_size: Connection pool size
        """
        self.db_url = db_url
        self.engine = None
        self.Session = None
        self._connect(pool_size)

    def _connect(self, pool_size: int, max_retries: int = 5):
        """
        Connect to database with retry logic

        Args:
            pool_size: Connection pool size
            max_retries: Maximum retry attempts
        """
        for attempt in range(max_retries):
            try:
                self.engine = create_engine(
                    self.db_url,
                    pool_size=pool_size,
                    pool_pre_ping=True,
                    pool_recycle=3600
                )

                # Test connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))

                self.Session = sessionmaker(bind=self.engine)
                logger.info("Successfully connected to DB2")
                return

            except Exception as e:
                wait_time = 2 ** attempt
                logger.error(f"Failed to connect to DB2 (attempt {attempt + 1}/{max_retries}): {str(e)}")

                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f"Failed to connect to DB2 after {max_retries} attempts")

    def health_check(self) -> bool:
        """
        Check database health

        Returns:
            True if healthy, False otherwise
        """
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def insert_article(self, data: dict) -> bool:
        """
        Insert article into DB2

        Args:
            data: Article data

        Returns:
            True if successful, False otherwise
        """
        session = self.Session()
        try:
            article = Article(
                id=data['id'],
                title=data['title'],
                content=data['content'],
                author=data['author'],
                category=data.get('category', 'general'),
                tags=data.get('tags', []),
                status=data.get('status', 'draft'),
                views_count=data.get('views_count', 0),
                created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else datetime.utcnow(),
                updated_at=datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None,
                published_at=datetime.fromisoformat(data['published_at'].replace('Z', '+00:00')) if data.get('published_at') else None
            )

            session.add(article)
            session.commit()

            logger.info(f"Article inserted into DB2: ID={article.id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error inserting article into DB2: {str(e)}")
            return False
        finally:
            session.close()

    def update_article(self, article_id: int, data: dict) -> bool:
        """
        Update article in DB2

        Args:
            article_id: Article ID
            data: Updated data

        Returns:
            True if successful, False otherwise
        """
        session = self.Session()
        try:
            article = session.query(Article).filter(Article.id == article_id).first()

            if not article:
                logger.warning(f"Article {article_id} not found in DB2 for update, creating it instead")
                # If article doesn't exist, insert it
                session.close()
                return self.insert_article(data)

            # Update fields
            article.title = data.get('title', article.title)
            article.content = data.get('content', article.content)
            article.author = data.get('author', article.author)
            article.category = data.get('category', article.category)
            article.tags = data.get('tags', article.tags)
            article.status = data.get('status', article.status)
            article.views_count = data.get('views_count', article.views_count)

            if data.get('updated_at'):
                article.updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00'))
            else:
                article.updated_at = datetime.utcnow()

            if data.get('published_at'):
                article.published_at = datetime.fromisoformat(data['published_at'].replace('Z', '+00:00'))

            session.commit()

            logger.info(f"Article updated in DB2: ID={article_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error updating article {article_id} in DB2: {str(e)}")
            return False
        finally:
            session.close()

    def delete_article(self, article_id: int) -> bool:
        """
        Delete article from DB2

        Args:
            article_id: Article ID

        Returns:
            True if successful, False otherwise
        """
        session = self.Session()
        try:
            article = session.query(Article).filter(Article.id == article_id).first()

            if not article:
                logger.warning(f"Article {article_id} not found in DB2 for deletion")
                return True  # Already deleted

            session.delete(article)
            session.commit()

            logger.info(f"Article deleted from DB2: ID={article_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting article {article_id} from DB2: {str(e)}")
            return False
        finally:
            session.close()

    def is_event_processed(self, event_id: str) -> bool:
        """
        Check if event has already been processed

        Args:
            event_id: Event ID

        Returns:
            True if already processed, False otherwise
        """
        session = self.Session()
        try:
            event = session.query(ProcessedEvent).filter(ProcessedEvent.event_id == event_id).first()
            return event is not None
        except Exception as e:
            logger.error(f"Error checking if event {event_id} is processed: {str(e)}")
            return False
        finally:
            session.close()

    def mark_event_processed(self, event_id: str, event_type: str, article_id: int, event_data: dict) -> bool:
        """
        Mark event as processed

        Args:
            event_id: Event ID
            event_type: Event type
            article_id: Article ID
            event_data: Event data

        Returns:
            True if successful, False otherwise
        """
        session = self.Session()
        try:
            processed_event = ProcessedEvent(
                event_id=event_id,
                event_type=event_type,
                article_id=article_id,
                event_data=event_data
            )

            session.add(processed_event)
            session.commit()

            logger.debug(f"Event marked as processed: {event_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error marking event {event_id} as processed: {str(e)}")
            return False
        finally:
            session.close()

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("DB2 connection closed")
