import logging
from datetime import datetime
from sqlalchemy import or_
from app.models.article import Article, ArticleStatus, db
from app.services.kafka_producer import KafkaProducerService

logger = logging.getLogger(__name__)


class ArticleService:
    """Service for managing articles"""

    def __init__(self, kafka_producer=None):
        """
        Initialize ArticleService

        Args:
            kafka_producer (KafkaProducerService): Kafka producer service
        """
        self.kafka_producer = kafka_producer

    def create_article(self, data):
        """
        Create a new article

        Args:
            data (dict): Article data

        Returns:
            Article: Created article

        Raises:
            Exception: If creation fails
        """
        try:
            article = Article(
                title=data.get('title'),
                content=data.get('content'),
                author=data.get('author'),
                category=data.get('category', 'general'),
                tags=data.get('tags', []),
                status=ArticleStatus.draft
            )

            db.session.add(article)
            db.session.commit()

            logger.info(f"Article created successfully: ID={article.id}, Title={article.title}")

            # Publish to Kafka
            if self.kafka_producer:
                self.kafka_producer.publish_article_created(article.to_dict())

            return article

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating article: {str(e)}")
            raise

    def get_article(self, article_id):
        """
        Get article by ID

        Args:
            article_id (int): Article ID

        Returns:
            Article: Article object or None if not found
        """
        return Article.query.get(article_id)

    def list_articles(self, page=1, per_page=10, filters=None):
        """
        List articles with pagination and filters

        Args:
            page (int): Page number
            per_page (int): Items per page
            filters (dict): Filter criteria

        Returns:
            tuple: (articles list, pagination info)
        """
        query = Article.query

        # Apply filters
        if filters:
            if filters.get('status'):
                try:
                    status = ArticleStatus(filters['status'])
                    query = query.filter(Article.status == status)
                except ValueError:
                    pass

            if filters.get('category'):
                query = query.filter(Article.category == filters['category'])

            if filters.get('author'):
                query = query.filter(Article.author == filters['author'])

        # Order by created_at descending
        query = query.order_by(Article.created_at.desc())

        # Paginate
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        page_info = {
            'current_page': pagination.page,
            'total_pages': pagination.pages,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

        return pagination.items, page_info

    def update_article(self, article_id, data):
        """
        Update an article

        Args:
            article_id (int): Article ID
            data (dict): Updated data

        Returns:
            Article: Updated article or None if not found

        Raises:
            Exception: If update fails
        """
        article = self.get_article(article_id)
        if not article:
            return None

        try:
            # Update fields
            if 'title' in data:
                article.title = data['title']
            if 'content' in data:
                article.content = data['content']
            if 'author' in data:
                article.author = data['author']
            if 'category' in data:
                article.category = data['category']
            if 'tags' in data:
                article.tags = data['tags']
            if 'status' in data:
                try:
                    article.status = ArticleStatus(data['status'])
                except ValueError:
                    logger.warning(f"Invalid status value: {data['status']}")

            article.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Article updated successfully: ID={article.id}")

            # Publish to Kafka
            if self.kafka_producer:
                self.kafka_producer.publish_article_updated(article.to_dict())

            return article

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating article {article_id}: {str(e)}")
            raise

    def delete_article(self, article_id):
        """
        Delete an article

        Args:
            article_id (int): Article ID

        Returns:
            bool: True if deleted, False if not found

        Raises:
            Exception: If deletion fails
        """
        article = self.get_article(article_id)
        if not article:
            return False

        try:
            article_data = article.to_dict()

            db.session.delete(article)
            db.session.commit()

            logger.info(f"Article deleted successfully: ID={article_id}")

            # Publish to Kafka
            if self.kafka_producer:
                self.kafka_producer.publish_article_deleted(article_data)

            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting article {article_id}: {str(e)}")
            raise

    def publish_article(self, article_id):
        """
        Publish an article (change status to PUBLISHED)

        Args:
            article_id (int): Article ID

        Returns:
            Article: Published article or None if not found

        Raises:
            Exception: If publish fails
        """
        article = self.get_article(article_id)
        if not article:
            return None

        try:
            article.status = ArticleStatus.published
            article.published_at = datetime.utcnow()
            article.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Article published successfully: ID={article_id}")

            # Publish to Kafka
            if self.kafka_producer:
                self.kafka_producer.publish_article_published(article.to_dict())

            return article

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error publishing article {article_id}: {str(e)}")
            raise

    def search_articles(self, query_string):
        """
        Search articles by title or content

        Args:
            query_string (str): Search query

        Returns:
            list: List of matching articles
        """
        search_pattern = f"%{query_string}%"
        articles = Article.query.filter(
            or_(
                Article.title.ilike(search_pattern),
                Article.content.ilike(search_pattern),
                Article.author.ilike(search_pattern)
            )
        ).all()

        return articles

    def increment_views(self, article_id):
        """
        Increment article view count

        Args:
            article_id (int): Article ID

        Returns:
            bool: True if successful, False otherwise
        """
        article = self.get_article(article_id)
        if not article:
            return False

        try:
            article.views_count += 1
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error incrementing views for article {article_id}: {str(e)}")
            return False
