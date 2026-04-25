from app.models import Article, Channel
from app.schemas import RegistrationDTO


def test_is_registration_pending(mocked_redis, cache_service, registration_dto):
    mocked_redis.get.return_value = None
    assert cache_service.is_registration_pending(registration_dto) is False

    mocked_redis.get.return_value = "present"
    assert cache_service.is_registration_pending(registration_dto) is True


def test_create_and_delete_pending_registration(mocked_redis, cache_service, registration_dto):
    mocked_redis.exists.side_effect = [False, True]

    cache_service.create_pending_registration(registration=registration_dto, code=111111)
    cache_service.delete_registration_from_pending(registration=registration_dto)

    mocked_redis.setex.assert_called_once()
    mocked_redis.delete.assert_called_once_with("reg:user@example.com")


def test_provided_code_correct(mocked_redis, cache_service):
    mocked_redis.get.return_value = (
        '{"code": 111111, "data": {"username": "username", "email": "user@example.com", "password": "password"}}'
    )

    result = cache_service.provided_code_correct("user@example.com", 111111)

    assert result == RegistrationDTO(username="username", email="user@example.com", password="password")
    mocked_redis.delete.assert_called_once_with("reg:user@example.com")


def test_set_and_get_available_channels(mocked_redis, cache_service):
    channels = [
        Channel(
            id=1,
            uuid="channel-uuid",
            title="Channel",
            link="https://example.com/feed",
            disabled_by_user=False,
            logo_url="https://example.com/logo.png"
        )
    ]
    mocked_redis.get.return_value = (
        '[{"id": 1, "uuid": "channel-uuid", "title": "Channel", "link": "https://example.com/feed", "logo_url": "https://example.com/logo.png", '
        ' "disabled_by_user": false}]'
    )

    cache_service.set_available_channels(channels, user_id=1)
    fetched_channels = cache_service.get_available_channels(user_id=1)

    mocked_redis.setex.assert_called_once()
    assert fetched_channels == channels


def test_set_and_get_article(mocked_redis, cache_service, article):
    mocked_redis.get.return_value = (
        '{"id": 1, "uuid": "article-uuid", "title": "Title", "link": "https://example.com/article",'
        ' "description": "Description", "pub_date": "2024-01-01T00:00:00+00:00",'
        ' "channel_link": "https://example.com/feed", "likes": 2, "liked_by_user": true,'
        ' "channel_logo": "https://example.com/logo.png"}'
    )

    cache_service.set_article(article)
    fetched_article = cache_service.get_article("article-uuid")

    mocked_redis.setex.assert_called_once()
    assert isinstance(fetched_article, Article)
    assert fetched_article.uuid == "article-uuid"


def test_rate_limit(mocked_redis, cache_service):
    mocked_redis.incr.side_effect = [1, 10, 11]

    assert cache_service.can_request_go_through("user-key") is True
    mocked_redis.expire.assert_called_once_with("user-key", 5)
    assert cache_service.can_request_go_through("user-key") is True
    assert cache_service.can_request_go_through("user-key") is False
