from abc import ABC, abstractmethod
from api.models import ArticleSearchEntry

class ElasticSearchInterface(ABC):
    @abstractmethod
    def save_article_entries(self, entries: list[ArticleSearchEntry]) -> None:
        ...

    @abstractmethod
    def delete_old_articles(self, hours: int = 72) -> None:
        ...

    @abstractmethod
    def search_articles(self, query: str, hours: int, disabled_channel_ids: list[int], page: int = 1) -> tuple[list[int], bool]:
        ...