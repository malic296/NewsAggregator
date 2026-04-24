from app.api_client.client import AuthenticatedClient
from app.api_client.api.articles import articles, article, like
from app.api_client.models import ArticleDTO
from typing import Optional
from .base_service import BaseService

class ArticlesService(BaseService):
    def __init__(self, client: AuthenticatedClient):
        self.client = client

    def read_articles(self, hours: Optional[int] = None) -> list[ArticleDTO]:
        response = articles.sync_detailed(
            client=self.client,
            hours=hours if hours else 1
        )

        self._handle_response(response)

        return response.parsed.articles if response.parsed.articles else []

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