from random import randint
from typing import Optional
from api.models import Channel, Article
from api.core.errors import MappingError
from api.schemas import RegistrationDTO
from redis import Redis
import json
from dataclasses import asdict
from api.interfaces import ValkeyInterface

class ValkeyRepository(ValkeyInterface):
    def __init__(self, client: Redis):
        self._reg_key_prefix = "reg:"
        self._data_key_prefix = "data:"
        self._client = client

    def is_registration_pending(self, registration: RegistrationDTO) -> bool:
        email_key = self._reg_key_prefix + registration.email

        data = self._client.get(email_key)
        return data is not None

    def delete_registration_from_pending(self, registration: RegistrationDTO) -> None:
        email_key = self._reg_key_prefix + registration.email

        if self._client.exists(email_key):
            self._client.delete(email_key)

    def create_pending_registration(self, registration: RegistrationDTO, code: int) -> None:
        email_key = self._reg_key_prefix + registration.email

        if not self._client.exists(email_key):
            dict_data = {
                "code": code,
                "data": registration.model_dump()
            }

            self._client.setex(email_key, 120, json.dumps(dict_data))

    def provided_code_correct(self, email: str, code: int) -> Optional[RegistrationDTO]:
        email_key = self._reg_key_prefix + email

        saved_data = self._client.get(email_key)
        if saved_data:
            json_data = json.loads(saved_data)

            if int(json_data["code"]) == code:
                self._client.delete(email_key)
                return RegistrationDTO(**json_data["data"])

        return None

    def set_available_channels(self, channels: list[Channel], user_id: int) -> None:
        channels_key = self._data_key_prefix + f"{user_id}:" + "available_channels"

        self._client.setex(channels_key, 600, json.dumps([asdict(channel) for channel in channels]))

    def invalidate_cache_channels(self, user_id: int) -> None:
        channels_key = self._data_key_prefix + f"{user_id}:" + "available_channels"
        self._client.delete(channels_key)

    def get_available_channels(self, user_id: int) -> list[Channel]:
        channels_key = self._data_key_prefix + f"{user_id}:" + "available_channels"

        saved_data = self._client.get(channels_key)
        if saved_data:
            json_data = json.loads(saved_data)
            try:
                return [Channel(**channel) for channel in json_data]
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="get_available_channels")

        return []

    def get_article(self, uuid: str) -> Optional[Article]:
        article_key = self._data_key_prefix + uuid
        saved_data = self._client.get(article_key)
        if saved_data:
            json_data = json.loads(saved_data)
            try:
                return Article(**json_data)
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="get_article")
        else:
            return None

    def set_article(self, article: Article) -> Optional[Article]:
        article_key = self._data_key_prefix + article.uuid
        try:
            article_dict = asdict(article)
            article_dict["pub_date"] = article_dict["pub_date"].isoformat()
            data = json.dumps(article_dict)
            self._client.setex(article_key, 600, data)

        except Exception as e:
            raise MappingError(mapping_error=str(e), method="set_article")

    def increment_counter(self, key: str) -> int:
        return self._client.incr(key)

    def set_expiration(self, key: str, seconds: int):
        self._client.expire(key, seconds)

    def generate_invite_code(self, consumer_id: int) -> int:
        key = f"invite_code:{consumer_id}"

        code = self._client.get(key)
        if not code:
            code = randint(100000, 999999)
            self._client.setex(key, 1800, code)

        return code

    def validate_invite_code(self, code: int) -> bool:
        for key in self._client.scan_iter("invite_code:*"):
            cached_value = self._client.get(key)
            if cached_value and int(cached_value) == code:
                return True
        return False