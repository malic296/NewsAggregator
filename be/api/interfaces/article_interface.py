from abc import ABC, abstractmethod
from typing import Optional
from api.models import Article, Consumer, PagedArticles, ArticleSearchEntry

class ArticleInterface(ABC):
    @abstractmethod
    def read_articles(self, consumer: Consumer, hours: int, order_by_likes: bool, sort_value: str | None, uuid: str | None) -> PagedArticles:
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
    def bulk_save_articles(self, articles: list[Article], channel_id_map: dict[str, int]) -> list[ArticleSearchEntry]:
        ...

    @abstractmethod
    def assign_new_themes(self, hours_limit: int = 72) -> None:
        ...
