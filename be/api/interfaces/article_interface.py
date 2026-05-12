from abc import ABC, abstractmethod
from typing import Optional
from api.models import Article, Consumer, PagedArticles, ArticleSearchEntry, ArticleWithChannelID
from api.models.enums import OrderByEnum

class ArticleInterface(ABC):
    @abstractmethod
    def read_articles(self, consumer: Consumer, hours: int, order_by: OrderByEnum, sort_value: str | None, uuid: str | None) -> PagedArticles:
        ...

    @abstractmethod
    def get_article(self, uuid: str) -> Optional[Article]:
        ...
    
    @abstractmethod
    def get_articles_by_ids(self, consumer: Consumer, ids: list[int]) -> list[Article]:
        ...

    @abstractmethod
    def like_article(self, article_id: int, consumer_id: int) -> bool:
        ...

    @abstractmethod
    def article_uuid_to_id(self, article_uuid: str) -> Optional[int]:
        ...

    @abstractmethod
    def get_unthemed_articles(self, hours: int) -> list[Article]:
        ...

    @abstractmethod
    def save_articles_unthemed(self, articles: list[ArticleWithChannelID]) -> list[ArticleSearchEntry]:
        ...

    @abstractmethod
    def delete_old_articles(self, hours: int = 96) -> None:
        ...