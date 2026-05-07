from api.interfaces.themes_interface import ThemesInterface
from api.models import Theme
from api.models import Consumer
from api.core.cursor import decode_cursor, encode_cursor
from api.models import PagedThemes

class ThemesService:
    def __init__(self, themes_repository: ThemesInterface):
        self.themes = themes_repository

    def get_themes(self, consumer: Consumer, cursor: str | None, page: int = 1, hours: int = 72) -> PagedThemes:
        sort_value, uuid = decode_cursor(cursor) if cursor else (None, None)

        themes: list[Theme] = self.themes.read_themes(consumer_id = consumer.id, hours = hours, sort_value=sort_value, uuid=uuid)
        has_more = len(themes) > 10
        return PagedThemes(
            themes=themes,
            next_cursor=encode_cursor(sort_value=sort_value, uuid=uuid) if has_more else None,
            has_more=has_more,
            next_page=2 if not page else page + 1 if has_more else None
        )