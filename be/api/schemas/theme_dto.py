from pydantic import BaseModel, Field
from datetime import datetime
from api.schemas.article_dto import ArticleDTO

class ThemeDTO(BaseModel):
    uuid: str
    newest_date: datetime
    articles: list[ArticleDTO] = Field(default_factory=list)