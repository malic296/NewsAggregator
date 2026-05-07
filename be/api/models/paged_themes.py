from dataclasses import dataclass
from api.models import Theme

@dataclass
class PagedThemes:
    themes: list[Theme]
    next_cursor: str | None = None
    next_page: int | None = None
    has_more: bool = False