from pydantic import BaseModel
from .article_dto import ArticleDTO

class PagedArticlesDTO(BaseModel):
    articles: list[ArticleDTO]
    next_cursor: str | None = None
    next_page: int | None = None
    has_more: bool = False