import uuid

from app.models import Channel
from app.core.errors import DatabaseError, MappingError
from app.models.scraped_data import ScrapedChannel
from .base_repository import BaseRepository
from app.interfaces import ChannelInterface

class ChannelRepository(BaseRepository, ChannelInterface):
    def get_channels(self, user_id: int) -> list[Channel]:
        query = """
            SELECT id, uuid, title, link, 
            EXISTS(
                SELECT 1 
                FROM disabled 
                WHERE consumer_id = %s AND channel_id = channel.id
            ) AS disabled_by_user
            FROM channel
        """
        params = (user_id, )
        db_result = self._execute(query=query, params=params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_channels"
            )

        try:
            return [Channel(**channel) for channel in db_result.data]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_channels")

    def set_disabled_channels_by_uuids(self, user_id: int, disabled_uuids: list[str]) -> None:
        inserts = [("DELETE FROM disabled WHERE consumer_id = %s", (user_id,))]

        query = """
            INSERT INTO disabled (consumer_id, channel_id) 
            SELECT %s, id
            FROM channel
            WHERE uuid = ANY(%s)
        """

        inserts.append((query, (user_id, disabled_uuids, )))

        db_result = self._execute_transaction(inserts)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="set_disabled_channels_by_uuids"
            )

    def update_channels(self, channels: list[ScrapedChannel]) -> None:
        article_queries: list[tuple[str, tuple]] = []

        for channel in channels:
            channel_sql = """
                INSERT INTO channel (title, link, uuid)
                VALUES (%s, %s, %s) ON CONFLICT (link) DO 
                UPDATE 
                SET title = EXCLUDED.title 
                RETURNING id; 
            """
            channel_params = (channel.title, channel.link, str(uuid.uuid4()))

            channel_result = self._execute(channel_sql, channel_params)

            if not channel_result.success:
                raise DatabaseError(message= channel_result.error_message if channel_result.error_message else "Unknown error", method="update_channels")

            if not channel_result.data:
                raise DatabaseError(f"Failed to fetch ID for channel {channel.title}", method="update_channels")

            channel_id = channel_result.data[0]["id"]

            for article in channel.articles:
                art_sql = """
                    INSERT INTO article (title, link, description, pub_date, channel_id, uuid)
                    VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (link) DO NOTHING; 
                """
                art_params = (
                    article.title,
                    article.link,
                    article.description,
                    str(article.pub_date),
                    channel_id,
                    article.uuid
                )
                article_queries.append((art_sql, art_params))

        if article_queries:
            articles_result = self._execute_transaction(article_queries)

            if not articles_result.success:
                raise DatabaseError(message= articles_result.error_message if articles_result.error_message else "Unknown error", method="update_channels")