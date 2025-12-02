import os
import logging
from typing import Optional, List
from datetime import datetime
from app.clients.rest_client import RestApiClient, RestApiError

logger = logging.getLogger(__name__)

# Initialize REST client
REST_API_URL = os.getenv('REST_API_URL', 'http://flask-api:5000')
rest_client = RestApiClient(REST_API_URL)


def _parse_article(data: dict):
    """
    Parse article data from REST API to GraphQL type

    Args:
        data: Article data from REST API

    Returns:
        Article object compatible with GraphQL schema
    """
    from app.schema import Article, ArticleStatus

    # Parse status
    status_str = data.get('status', 'draft')
    try:
        status = ArticleStatus(status_str)
    except ValueError:
        status = ArticleStatus.DRAFT

    # Parse datetime fields
    created_at = datetime.fromisoformat(data['created_at'].replace('Z', '+00:00')) if data.get('created_at') else datetime.utcnow()
    updated_at = datetime.fromisoformat(data['updated_at'].replace('Z', '+00:00')) if data.get('updated_at') else None
    published_at = datetime.fromisoformat(data['published_at'].replace('Z', '+00:00')) if data.get('published_at') else None

    return Article(
        id=str(data['id']),
        title=data['title'],
        content=data['content'],
        author=data['author'],
        category=data.get('category'),
        tags=data.get('tags', []),
        status=status,
        views_count=data.get('views_count', 0),
        created_at=created_at,
        updated_at=updated_at,
        published_at=published_at
    )


async def get_article(article_id: int):
    """
    Get a single article by ID

    Args:
        article_id: Article ID

    Returns:
        Article or None if not found
    """
    try:
        data = await rest_client.get_article(article_id)
        if not data:
            return None

        return _parse_article(data)

    except RestApiError as e:
        logger.error(f"Error fetching article {article_id}: {e.message}")
        raise Exception(f"Failed to fetch article: {e.message}")


async def get_articles(page: int, per_page: int, filter_input):
    """
    Get paginated list of articles

    Args:
        page: Page number
        per_page: Items per page
        filter_input: Filter criteria

    Returns:
        ArticleConnection with items and page_info
    """
    from app.schema import ArticleConnection, PageInfo

    try:
        # Build filters
        filters = {}
        if filter_input:
            if filter_input.status:
                filters['status'] = filter_input.status.value
            if filter_input.category:
                filters['category'] = filter_input.category
            if filter_input.author:
                filters['author'] = filter_input.author

        # Fetch from REST API
        data = await rest_client.list_articles(page=page, per_page=per_page, filters=filters)

        # Parse articles
        articles = [_parse_article(item) for item in data.get('items', [])]

        # Parse page info
        page_info_data = data.get('page_info', {})
        page_info = PageInfo(
            current_page=page_info_data.get('current_page', page),
            total_pages=page_info_data.get('total_pages', 1),
            per_page=page_info_data.get('per_page', per_page),
            total_items=page_info_data.get('total_items', 0),
            has_next=page_info_data.get('has_next', False),
            has_prev=page_info_data.get('has_prev', False)
        )

        return ArticleConnection(items=articles, page_info=page_info)

    except RestApiError as e:
        logger.error(f"Error fetching articles: {e.message}")
        raise Exception(f"Failed to fetch articles: {e.message}")


async def search_articles(query: str):
    """
    Search articles by query string

    Args:
        query: Search query

    Returns:
        List of matching articles
    """
    try:
        results = await rest_client.search_articles(query)
        return [_parse_article(item) for item in results]

    except RestApiError as e:
        logger.error(f"Error searching articles: {e.message}")
        raise Exception(f"Failed to search articles: {e.message}")


async def create_article(input_data):
    """
    Create a new article

    Args:
        input_data: Article input data

    Returns:
        Created article
    """
    try:
        # Convert input to dict
        data = {
            'title': input_data.title,
            'content': input_data.content,
            'author': input_data.author,
            'category': input_data.category or 'general',
            'tags': input_data.tags or []
        }

        # Create via REST API
        result = await rest_client.create_article(data)
        return _parse_article(result)

    except RestApiError as e:
        logger.error(f"Error creating article: {e.message}")
        raise Exception(f"Failed to create article: {e.message}")


async def update_article(article_id: int, input_data):
    """
    Update an article

    Args:
        article_id: Article ID
        input_data: Updated data

    Returns:
        Updated article or None if not found
    """
    try:
        # Convert input to dict (only include provided fields)
        data = {}
        if input_data.title is not None:
            data['title'] = input_data.title
        if input_data.content is not None:
            data['content'] = input_data.content
        if input_data.author is not None:
            data['author'] = input_data.author
        if input_data.category is not None:
            data['category'] = input_data.category
        if input_data.tags is not None:
            data['tags'] = input_data.tags
        if input_data.status is not None:
            data['status'] = input_data.status.value

        # Update via REST API
        result = await rest_client.update_article(article_id, data)
        if not result:
            return None

        return _parse_article(result)

    except RestApiError as e:
        logger.error(f"Error updating article {article_id}: {e.message}")
        raise Exception(f"Failed to update article: {e.message}")


async def delete_article(article_id: int) -> bool:
    """
    Delete an article

    Args:
        article_id: Article ID

    Returns:
        True if deleted, False if not found
    """
    try:
        return await rest_client.delete_article(article_id)

    except RestApiError as e:
        logger.error(f"Error deleting article {article_id}: {e.message}")
        raise Exception(f"Failed to delete article: {e.message}")


async def publish_article(article_id: int):
    """
    Publish an article

    Args:
        article_id: Article ID

    Returns:
        Published article or None if not found
    """
    try:
        result = await rest_client.publish_article(article_id)
        if not result:
            return None

        return _parse_article(result)

    except RestApiError as e:
        logger.error(f"Error publishing article {article_id}: {e.message}")
        raise Exception(f"Failed to publish article: {e.message}")
