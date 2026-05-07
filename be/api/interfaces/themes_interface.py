from abc import ABC, abstractmethod
from api.models import Theme

class ThemesInterface(ABC):
    @abstractmethod
    def read_themes(self, consumer_id: int, sort_value: str | None, uuid: str | None, hours: int = 72)  -> list[Theme]:
        ...