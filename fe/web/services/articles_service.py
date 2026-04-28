from web.api_client.client import AuthenticatedClient
from web.api_client.api.articles import articles, article, like
from web.api_client.models import PagedArticlesDTO, ArticleDTO
from typing import Optional
from .base_service import BaseService

class ArticlesService(BaseService):
    def __init__(self, client: AuthenticatedClient):
        self.client = client

    def read_articles(self, hours: int = 1, order_by_likes: bool = True, cursor: Optional[str] = None, page: Optional[int] = None, query: Optional[str] = None) -> PagedArticlesDTO:
        response = articles.sync_detailed(
            client=self.client,
            hours=hours,
            order_by_likes=order_by_likes,
            cursor=cursor,
            query=query,
            page=page
        )

        self._handle_response(response)

        return response.parsed

    def read_article(self, uuid: str) -> Optional[ArticleDTO]:
        response = article.sync_detailed(
            client=self.client,
            uuid=uuid,
        )

        self._handle_response(response)

        return response.parsed.article

    def like_article(self, uuid: str) -> bool:
        response = like.sync_detailed(
            client=self.client,
            article_uuid=uuid
        )

        self._handle_response(response)

        return response.parsed.liked