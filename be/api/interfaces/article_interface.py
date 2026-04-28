from abc import ABC, abstractmethod
from typing import Optional
from api.models import Article, Consumer, PagedArticles

class ArticleInterface(ABC):
    @abstractmethod
    def get_articles(self, consumer: Consumer, hours: int, order_by_likes: bool, sort_value: str | None, uuid: str | None) -> PagedArticles:
        ...

    @abstractmethod
    def get_article(self, uuid: str) -> Optional[Article]:
        ...
    
    @abstractmethod
    def article_uuid_to_id(self, article_uuid: str) -> Optional[int]:
        ...

    @abstractmethod
    def like_article(self, article_id: int, consumer_id: int) -> bool:
        ...

    @abstractmethod
    def get_articles_by_ids(self, consumer: Consumer, ids: list[int]) -> list[Article]:
        ...
