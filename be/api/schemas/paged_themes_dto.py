from pydantic import BaseModel
from .theme_dto import ThemeDTO

class PagedThemesDTO(BaseModel):
    themes: list[ThemeDTO]
    next_cursor: str | None = None
    next_page: int | None = None
    has_more: bool = False