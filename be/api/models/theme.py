from dataclasses import dataclass, field
from datetime import datetime
from .article import Article

@dataclass
class Theme:
    uuid: str
    newest_date: datetime
    articles: list[Article] = field(default_factory=list)
    id: int | None = None