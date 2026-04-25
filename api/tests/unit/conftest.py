from datetime import datetime, timezone
import logging

import pytest

from app.models import Article, Channel, Consumer, DBResult
from app.repositories import ArticleRepository, ChannelRepository, ConsumerRepository, LoggingRepository
from app.schemas import RegistrationDTO, UpdateCredentialsDTO
from app.services import CacheService, EmailService, SecurityService


@pytest.fixture
def consumer() -> Consumer:
    return Consumer(id=1, uuid="consumer-uuid", username="username", email="user@example.com")


@pytest.fixture
def article() -> Article:
    return Article(
        id=1,
        uuid="article-uuid",
        title="Title",
        link="https://example.com/article",
        description="Description",
        pub_date=datetime.now(timezone.utc),
        channel_link="https://example.com/feed",
        likes=2,
        liked_by_user=True,
        channel_logo="https://example.com/logo.png"
    )


@pytest.fixture
def channel() -> Channel:
    return Channel(
        id=1,
        uuid="channel-uuid",
        title="Channel",
        link="https://example.com/feed",
        disabled_by_user=False,
        logo_url="https://example.com/logo.png"
    )


@pytest.fixture
def registration_dto() -> RegistrationDTO:
    return RegistrationDTO(username="username", email="user@example.com", password="password")


@pytest.fixture
def update_credentials_dto() -> UpdateCredentialsDTO:
    return UpdateCredentialsDTO(
        old_password="old-password",
        new_password="new-password",
        new_username="new-username",
    )


@pytest.fixture
def email_service() -> EmailService:
    return EmailService(resend_key="test-key")


@pytest.fixture
def security_service() -> SecurityService:
    return SecurityService(pepper="eJrCp9t7z3+BJmqlyzuSqt3yvW8EvtHQz5bjv61HcR0=", jwt="eJrCp9t7z3+BJmqlyzuSqt3yvW8EvtHQz5bjv61HcR0=")


@pytest.fixture
def mocked_redis(mocker):
    redis_instance = mocker.Mock()
    redis_instance.ping.return_value = True
    mocker.patch("app.services.cache_service.Redis", return_value=redis_instance)
    return redis_instance


@pytest.fixture
def cache_service(mocked_redis) -> CacheService:
    return CacheService(host="localhost", port=6379, db=0)


@pytest.fixture
def article_repository(mocker):
    pool = mocker.Mock()
    return ArticleRepository(connection_pool=pool)


@pytest.fixture
def channel_repository(mocker):
    pool = mocker.Mock()
    return ChannelRepository(connection_pool=pool)


@pytest.fixture
def consumer_repository(mocker):
    pool = mocker.Mock()
    return ConsumerRepository(connection_pool=pool)


@pytest.fixture
def logging_repository(mocker):
    pool = mocker.Mock()
    return LoggingRepository(connection_pool=pool)


@pytest.fixture
def db_result_article(article: Article) -> DBResult:
    return DBResult(success=True, data=[article.__dict__], row_count=1)


@pytest.fixture
def db_result_channels(channel: Channel) -> DBResult:
    return DBResult(success=True, data=[channel.__dict__], row_count=1)


@pytest.fixture
def db_result_consumer(consumer: Consumer) -> DBResult:
    return DBResult(success=True, data=[consumer.__dict__], row_count=1)


@pytest.fixture
def invalid_db_result() -> DBResult:
    return DBResult(success=False, error_message="db failed", data=None, row_count=0)


@pytest.fixture
def log_record() -> logging.LogRecord:
    record = logging.LogRecord(
        name="tests.logger",
        level=logging.ERROR,
        pathname=__file__,
        lineno=10,
        msg="test log message",
        args=(),
        exc_info=None,
        func="test_func",
    )
    record.method = "test_method"
    return record
