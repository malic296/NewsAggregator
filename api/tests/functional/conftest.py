from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from app.core.container import ServiceContainer
from app.models import Article, Channel, Consumer
from app.services import SecurityService
from run import app


@pytest.fixture
def consumer() -> Consumer:
    return Consumer(id=1, uuid="consumer-uuid", username="username", email="user@example.com")


@pytest.fixture
def functional_services(mocker, consumer: Consumer):
    security_service = SecurityService(pepper="eJrCp9t7z3+BJmqlyzuSqt3yvW8EvtHQz5bjv61HcR0=", jwt="eJrCp9t7z3+BJmqlyzuSqt3yvW8EvtHQz5bjv61HcR0=")
    article = Article(
        id=1,
        uuid="article-uuid",
        title="Title",
        link="https://example.com/article",
        description="Description",
        pub_date=datetime.now(timezone.utc),
        channel_link="https://example.com/feed",
        likes=0,
        liked_by_user=False,
        channel_logo="https://example.com/logo.png"
    )
    channel = Channel(
        id=1,
        uuid="channel-uuid",
        title="Channel",
        link="https://example.com/feed",
        disabled_by_user=False,
        logo_url="https://example.com/logo.png",
        feed_url="https://example.com/feed.xml"
    )

    container = ServiceContainer(
        article_service=mocker.Mock(),
        channel_service=mocker.Mock(),
        consumer_service=mocker.Mock(),
        cache_service=mocker.Mock(),
        email_service=mocker.Mock(),
        security_service=security_service,
    )
    container.cache_service.can_request_go_through.return_value = True
    container.article_service.get_articles.return_value = [article]
    container.article_service.get_article.return_value = article
    container.article_service.like_article.return_value = True
    container.channel_service.get_channels.return_value = [channel]
    container.consumer_service.get_consumer_by_credential.return_value = consumer
    container.consumer_service.authenticate.return_value = security_service.create_access_token(consumer)
    container.consumer_service.verify_registration.return_value = security_service.create_access_token(consumer)

    app.dependency_overrides.clear()
    app.state.services = container
    return container


@pytest.fixture
def client(functional_services):
    return TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


@pytest.fixture
def auth_headers(functional_services, consumer: Consumer):
    token = functional_services.security_service.create_access_token(consumer)
    return {"Authorization": f"Bearer {token}"}
