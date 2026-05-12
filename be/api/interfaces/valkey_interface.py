from abc import ABC, abstractmethod
from typing import Optional
from api.models import Article, Channel
from api.schemas import RegistrationDTO

class ValkeyInterface(ABC):
    @abstractmethod
    def is_registration_pending(self, registration: RegistrationDTO) -> bool:
        ...

    @abstractmethod
    def delete_registration_from_pending(self, registration: RegistrationDTO) -> None:
        ...

    @abstractmethod
    def create_pending_registration(self, registration: RegistrationDTO, code: int) -> None:
        ...

    @abstractmethod
    def provided_code_correct(self, email: str, code: int) -> Optional[RegistrationDTO]:
        ...

    @abstractmethod
    def set_available_channels(self, channels: list[Channel], user_id: int) -> None:
        ...

    @abstractmethod
    def invalidate_cache_channels(self, user_id: int) -> None:
        ...

    @abstractmethod
    def get_available_channels(self, user_id: int) -> list[Channel]:
        ...

    @abstractmethod
    def get_article(self, uuid: str) -> Optional[Article]:
        ...

    @abstractmethod
    def set_article(self, article: Article) -> Optional[Article]:
        ...

    @abstractmethod
    def increment_counter(self, key: str) -> int:
        ...

    @abstractmethod
    def set_expiration(self, key: str, seconds: int):
        ...

    @abstractmethod
    def generate_invite_code(self, consumer_id: int) -> int:
        ...

    @abstractmethod
    def validate_invite_code(self, code: int) -> bool:
        ...
