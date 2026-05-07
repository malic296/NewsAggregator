import logging
from api.models import Consumer, Article, Channel
from api.interfaces import ArticleInterface, ElasticSearchInterface, ChannelInterface
from api.core.errors import ArticleNotFoundError
from api.core.cursor import decode_cursor
from api.interfaces import ValkeyInterface
from api.models import PagedArticles, Channel

logger = logging.getLogger(__name__)

class ArticleService:
    def __init__(self, articles: ArticleInterface, valkey: ValkeyInterface, elasticsearch: ElasticSearchInterface, channels = ChannelInterface):
        self.articles = articles
        self.channels = channels
        self.valkey = valkey
        self.elasticsearch = elasticsearch

    def get_articles(self, consumer: Consumer, hours: int, order_by_likes: bool, cursor: str | None, page: int = 1, query: str | None = None) -> PagedArticles:
        if hours > 72 or hours < 1:
            raise Exception("Hours must be <= 1 and 72 <=")

        if query:
            disabled_ids: list[int] = self.channels.get_disabled_channel_ids_for_user(consumer_id=consumer.id)

            ids, has_more = self.elasticsearch.search_articles(query=query, hours=hours, disabled_channel_ids=disabled_ids, page=page)

            if not ids:
                return PagedArticles(articles=[], has_more=False)

            articles = self.articles.get_articles_by_ids(ids=ids, consumer=consumer)
            article_map = {a.id: a for a in articles}
            ordered = [article_map[id] for id in ids if id in article_map]
            return PagedArticles(articles=ordered, has_more=has_more, next_page=page + 1 if has_more else None)

        sort_value, uuid = decode_cursor(cursor) if cursor else (None, None)

        return self.articles.read_articles(
            consumer=consumer,
            hours=hours,
            order_by_likes=order_by_likes,
            sort_value=sort_value,
            uuid=uuid
        )

    def get_article(self, uuid: str) -> Article:
        article = self.valkey.get_article(uuid=uuid)
        if not article:
            article = self.articles.get_article(uuid=uuid)
            if article:
                self.valkey.set_article(article=article)

        if not article:
            raise ArticleNotFoundError()

        return article

    def like_article(self, article_uuid: str, consumer: Consumer) -> bool:
        article_id = self.articles.article_uuid_to_id(article_uuid)
        if not article_id:
            raise ArticleNotFoundError()

        return self.articles.like_article(article_id=article_id, consumer_id=consumer.id)