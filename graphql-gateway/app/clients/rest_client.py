import httpx
import logging
from typing import Optional, Dict, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class RestApiError(Exception):
    """Custom exception for REST API errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class RestApiClient:
    """HTTP client for Flask REST API"""

    def __init__(self, base_url: str, timeout: float = 10.0):
        """
        Initialize REST API client

        Args:
            base_url: Base URL of the Flask API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(f"REST API client initialized with base URL: {base_url}")

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None
    ) -> Dict:
        """
        Make HTTP request with retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path
            params: Query parameters
            json: JSON body

        Returns:
            Response data as dictionary

        Raises:
            RestApiError: If request fails
        """
        url = f"{self.base_url}{path}"

        try:
            logger.debug(f"{method} {url} - params: {params}, json: {json}")

            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json
            )

            # Check for HTTP errors
            if response.status_code >= 400:
                error_message = f"HTTP {response.status_code}"
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', error_message)
                except:
                    pass

                logger.error(f"API error: {error_message} (status: {response.status_code})")
                raise RestApiError(error_message, response.status_code)

            # Return JSON response
            return response.json()

        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise RestApiError(f"Request failed: {str(e)}", 503)

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise RestApiError(f"Unexpected error: {str(e)}", 500)

    async def get_article(self, article_id: int) -> Optional[Dict]:
        """
        Get a single article by ID

        Args:
            article_id: Article ID

        Returns:
            Article data or None if not found
        """
        try:
            return await self._make_request('GET', f'/api/v1/articles/{article_id}')
        except RestApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def list_articles(
        self,
        page: int = 1,
        per_page: int = 10,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        List articles with pagination and filters

        Args:
            page: Page number
            per_page: Items per page
            filters: Filter criteria

        Returns:
            Dictionary with items and page_info
        """
        params = {
            'page': page,
            'per_page': per_page
        }

        if filters:
            params.update(filters)

        return await self._make_request('GET', '/api/v1/articles', params=params)

    async def create_article(self, data: Dict) -> Dict:
        """
        Create a new article

        Args:
            data: Article data

        Returns:
            Created article data
        """
        return await self._make_request('POST', '/api/v1/articles', json=data)

    async def update_article(self, article_id: int, data: Dict) -> Optional[Dict]:
        """
        Update an article

        Args:
            article_id: Article ID
            data: Updated data

        Returns:
            Updated article data or None if not found
        """
        try:
            return await self._make_request('PUT', f'/api/v1/articles/{article_id}', json=data)
        except RestApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def delete_article(self, article_id: int) -> bool:
        """
        Delete an article

        Args:
            article_id: Article ID

        Returns:
            True if deleted, False if not found
        """
        try:
            await self._make_request('DELETE', f'/api/v1/articles/{article_id}')
            return True
        except RestApiError as e:
            if e.status_code == 404:
                return False
            raise

    async def publish_article(self, article_id: int) -> Optional[Dict]:
        """
        Publish an article

        Args:
            article_id: Article ID

        Returns:
            Published article data or None if not found
        """
        try:
            return await self._make_request('POST', f'/api/v1/articles/{article_id}/publish')
        except RestApiError as e:
            if e.status_code == 404:
                return None
            raise

    async def search_articles(self, query: str) -> List[Dict]:
        """
        Search articles

        Args:
            query: Search query

        Returns:
            List of matching articles
        """
        result = await self._make_request('GET', '/api/v1/articles/search', params={'q': query})
        return result.get('results', [])
