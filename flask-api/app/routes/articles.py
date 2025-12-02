from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.article_schema import (
    ArticleCreateSchema,
    ArticleUpdateSchema,
    ArticleResponseSchema,
    ArticleListSchema
)
from app.services.article_service import ArticleService
from app.utils.metrics import track_request
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
articles_bp = Blueprint('articles', __name__, url_prefix='/api/v1')

# Initialize schemas
article_create_schema = ArticleCreateSchema()
article_update_schema = ArticleUpdateSchema()
article_response_schema = ArticleResponseSchema()
article_list_schema = ArticleListSchema()


def get_article_service():
    """Get ArticleService instance from app context"""
    from flask import current_app
    return current_app.article_service


@articles_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'flask-api'
    }), 200


@articles_bp.route('/articles', methods=['GET'])
@track_request
def list_articles():
    """
    List articles with pagination and filters

    Query params:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 10, max: 100)
        - status (str): Filter by status (draft/published/archived)
        - category (str): Filter by category
        - author (str): Filter by author

    Returns:
        JSON response with articles and pagination info
    """
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)

    filters = {}
    if request.args.get('status'):
        filters['status'] = request.args.get('status')
    if request.args.get('category'):
        filters['category'] = request.args.get('category')
    if request.args.get('author'):
        filters['author'] = request.args.get('author')

    # Get articles
    service = get_article_service()
    articles, page_info = service.list_articles(page=page, per_page=per_page, filters=filters)

    # Serialize response
    response = article_list_schema.dump({
        'items': articles,
        'page_info': page_info
    })

    return jsonify(response), 200


@articles_bp.route('/articles/<int:article_id>', methods=['GET'])
@track_request
def get_article(article_id):
    """
    Get a single article by ID

    Args:
        article_id (int): Article ID

    Returns:
        JSON response with article data or 404 if not found
    """
    service = get_article_service()
    article = service.get_article(article_id)

    if not article:
        return jsonify({'error': 'Article not found'}), 404

    # Increment view count
    service.increment_views(article_id)

    response = article_response_schema.dump(article)
    return jsonify(response), 200


@articles_bp.route('/articles', methods=['POST'])
@track_request
def create_article():
    """
    Create a new article

    Request body:
        - title (str, required): Article title
        - content (str, required): Article content
        - author (str, required): Author name
        - category (str, optional): Category (default: 'general')
        - tags (list, optional): List of tags

    Returns:
        JSON response with created article or validation errors
    """
    try:
        # Validate request data
        data = article_create_schema.load(request.json)

        # Create article
        service = get_article_service()
        article = service.create_article(data)

        # Serialize response
        response = article_response_schema.dump(article)
        return jsonify(response), 201

    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Error creating article: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@articles_bp.route('/articles/<int:article_id>', methods=['PUT'])
@track_request
def update_article(article_id):
    """
    Update an article (full update)

    Args:
        article_id (int): Article ID

    Request body: Same as create_article (all fields optional)

    Returns:
        JSON response with updated article or error
    """
    try:
        # Validate request data
        data = article_update_schema.load(request.json)

        # Update article
        service = get_article_service()
        article = service.update_article(article_id, data)

        if not article:
            return jsonify({'error': 'Article not found'}), 404

        # Serialize response
        response = article_response_schema.dump(article)
        return jsonify(response), 200

    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400
    except Exception as e:
        logger.error(f"Error updating article: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@articles_bp.route('/articles/<int:article_id>', methods=['PATCH'])
@track_request
def patch_article(article_id):
    """
    Partially update an article

    Args:
        article_id (int): Article ID

    Request body: Any subset of article fields

    Returns:
        JSON response with updated article or error
    """
    return update_article(article_id)  # Same logic as PUT for this implementation


@articles_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@track_request
def delete_article(article_id):
    """
    Delete an article

    Args:
        article_id (int): Article ID

    Returns:
        204 No Content on success, 404 if not found
    """
    try:
        service = get_article_service()
        deleted = service.delete_article(article_id)

        if not deleted:
            return jsonify({'error': 'Article not found'}), 404

        return '', 204

    except Exception as e:
        logger.error(f"Error deleting article: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@articles_bp.route('/articles/<int:article_id>/publish', methods=['POST'])
@track_request
def publish_article(article_id):
    """
    Publish an article (change status to PUBLISHED)

    Args:
        article_id (int): Article ID

    Returns:
        JSON response with published article or error
    """
    try:
        service = get_article_service()
        article = service.publish_article(article_id)

        if not article:
            return jsonify({'error': 'Article not found'}), 404

        # Serialize response
        response = article_response_schema.dump(article)
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error publishing article: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@articles_bp.route('/articles/search', methods=['GET'])
@track_request
def search_articles():
    """
    Search articles by query string

    Query params:
        - q (str, required): Search query

    Returns:
        JSON response with matching articles
    """
    query = request.args.get('q', '').strip()

    if not query:
        return jsonify({'error': 'Query parameter "q" is required'}), 400

    service = get_article_service()
    articles = service.search_articles(query)

    response = {
        'query': query,
        'count': len(articles),
        'results': [article_response_schema.dump(article) for article in articles]
    }

    return jsonify(response), 200
