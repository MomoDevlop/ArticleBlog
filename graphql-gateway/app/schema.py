import strawberry
from typing import List, Optional
from datetime import datetime
from enum import Enum
from app.resolvers.article_resolver import (
    get_article,
    get_articles,
    search_articles,
    create_article,
    update_article,
    delete_article,
    publish_article
)


class ArticleStatusEnum(str, Enum):
    """Article status enumeration"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


ArticleStatus = strawberry.enum(ArticleStatusEnum)


@strawberry.type
class Article:
    """Article type"""
    id: strawberry.ID
    title: str
    content: str
    author: str
    category: Optional[str] = None
    tags: List[str] = strawberry.field(default_factory=list)
    status: ArticleStatus = ArticleStatus.DRAFT
    views_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None


@strawberry.type
class PageInfo:
    """Pagination information"""
    current_page: int
    total_pages: int
    per_page: int
    total_items: int
    has_next: bool
    has_prev: bool


@strawberry.type
class ArticleConnection:
    """Paginated articles"""
    items: List[Article]
    page_info: PageInfo


@strawberry.input
class ArticleInput:
    """Input for creating an article"""
    title: str
    content: str
    author: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = strawberry.field(default_factory=list)


@strawberry.input
class ArticleUpdateInput:
    """Input for updating an article"""
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[ArticleStatus] = None


@strawberry.input
class ArticleFilterInput:
    """Input for filtering articles"""
    status: Optional[ArticleStatus] = None
    category: Optional[str] = None
    author: Optional[str] = None


@strawberry.type
class Query:
    """GraphQL queries"""

    @strawberry.field
    async def article(self, id: strawberry.ID) -> Optional[Article]:
        """
        Get a single article by ID

        Args:
            id: Article ID

        Returns:
            Article or None if not found
        """
        return await get_article(int(id))

    @strawberry.field
    async def articles(
        self,
        page: int = 1,
        per_page: int = 10,
        filter: Optional[ArticleFilterInput] = None
    ) -> ArticleConnection:
        """
        Get paginated list of articles

        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 10)
            filter: Filter criteria

        Returns:
            ArticleConnection with items and pagination info
        """
        return await get_articles(page, per_page, filter)

    @strawberry.field
    async def search_articles(self, query: str) -> List[Article]:
        """
        Search articles by query string

        Args:
            query: Search query

        Returns:
            List of matching articles
        """
        return await search_articles(query)


@strawberry.type
class Mutation:
    """GraphQL mutations"""

    @strawberry.mutation
    async def create_article(self, input: ArticleInput) -> Article:
        """
        Create a new article

        Args:
            input: Article input data

        Returns:
            Created article
        """
        return await create_article(input)

    @strawberry.mutation
    async def update_article(
        self,
        id: strawberry.ID,
        input: ArticleUpdateInput
    ) -> Optional[Article]:
        """
        Update an article

        Args:
            id: Article ID
            input: Updated data

        Returns:
            Updated article or None if not found
        """
        return await update_article(int(id), input)

    @strawberry.mutation
    async def delete_article(self, id: strawberry.ID) -> bool:
        """
        Delete an article

        Args:
            id: Article ID

        Returns:
            True if deleted, False if not found
        """
        return await delete_article(int(id))

    @strawberry.mutation
    async def publish_article(self, id: strawberry.ID) -> Optional[Article]:
        """
        Publish an article (change status to PUBLISHED)

        Args:
            id: Article ID

        Returns:
            Published article or None if not found
        """
        return await publish_article(int(id))


# Create GraphQL schema
schema = strawberry.Schema(query=Query, mutation=Mutation)
