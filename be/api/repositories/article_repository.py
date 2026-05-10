from typing import Optional
from .base_repository import BaseRepository
from api.interfaces.article_interface import ArticleInterface
from datetime import datetime, timezone, timedelta
from api.models import Consumer, Article, PagedArticles, ArticleSearchEntry, ArticleWithChannelID
from api.core.errors import MappingError, DatabaseError
from api.core.cursor import encode_cursor

class ArticleRepository(BaseRepository, ArticleInterface):
    def read_articles(self, consumer: Consumer, hours: int, order_by_likes: bool, sort_value: str | int | None, uuid: str | None) -> PagedArticles:
        date_since = datetime.now(timezone.utc) - timedelta(hours=hours)
        inner_query = """
            SELECT 
                a.uuid, a.title, a.description, a.link, a.pub_date,
                c.link      AS channel_link,
                c.logo_url  AS channel_logo, 
                COUNT(l.id) AS likes,
                EXISTS(
                    SELECT 1 FROM likes
                    WHERE article_id = a.id AND consumer_id = %s
                ) AS liked_by_user
            FROM article AS a 
            JOIN channel AS c on c.id = a.channel_id
            LEFT JOIN likes as l ON a.id = l.article_id
            WHERE a.pub_date >= %s
                AND a.channel_id NOT IN (
                    SELECT channel_id from disabled WHERE consumer_id = %s
                )
            GROUP BY a.id, c.link, c.logo_url
        """

        params = [consumer.id, date_since, consumer.id]

        cursor_filter = ""
        if sort_value is not None and uuid is not None:
            if order_by_likes:
                cursor_filter = """
                    WHERE (likes < %s OR (likes = %s AND uuid < %s))
                """
                params.extend([sort_value, sort_value, uuid])
            else:
                cursor_dt = datetime.fromisoformat(sort_value) if isinstance(sort_value, str) else sort_value
                cursor_filter = "WHERE (pub_date < %s OR (pub_date = %s AND uuid < %s))"
                params.extend([cursor_dt, cursor_dt, uuid])

        order = "ORDER BY likes DESC, uuid DESC" if order_by_likes else "ORDER BY pub_date DESC, uuid DESC"
        params.append(self.PAGE_SIZE + 1)

        query = f"""
            SELECT * FROM (
                {inner_query}
            ) AS subquery {cursor_filter} {order} LIMIT %s
        """

        db_result = self._execute(query, tuple(params))
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message or "Unknown error",
                method="get_articles"
            )

        try:
            rows = db_result.data
            has_more = len(rows) > self.PAGE_SIZE
            rows = rows[:self.PAGE_SIZE]

            articles = [Article(**row) for row in rows]

            next_cursor = None
            if has_more:
                last = articles[-1]
                sort_val = last.likes if order_by_likes else last.pub_date.replace(tzinfo=None)
                next_cursor = encode_cursor(sort_value=sort_val, uuid=last.uuid)

            return PagedArticles(
                articles=articles,
                next_cursor=next_cursor,
                has_more=has_more
            )

        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_articles")

    def get_articles_by_ids(self, consumer: Consumer, ids: list[int]) -> list[Article]:
        if not ids:
            return []

        placeholders = ",".join(["%s"] * len(ids))

        query = f"""
            SELECT 
                a.id, a.uuid, a.title, a.description, a.link, a.pub_date,
                c.link      AS channel_link,
                c.logo_url  AS channel_logo, 
                COUNT(l.id) AS likes,
                EXISTS(
                    SELECT 1 FROM likes
                    WHERE article_id = a.id AND consumer_id = %s
                ) AS liked_by_user
            FROM article AS a 
            JOIN channel AS c on c.id = a.channel_id
            LEFT JOIN likes as l ON a.id = l.article_id
            WHERE a.id IN ({placeholders})
            GROUP BY a.id, c.link, c.logo_url
        """

        result = self._execute(query, (consumer.id, *ids))

        if not result.success:
            raise DatabaseError(
                message=result.error_message if result.error_message else "Unknown error",
                method="get_articles_by_ids"
            )

        try:
            return [Article(**row) for row in (result.data if result.data else [])]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_articles_by_ids")

    def get_article(self, uuid: str) -> Optional[Article]:
        query = """
            SELECT 
                a.id AS id, 
                a.uuid AS uuid, 
                a.title AS title, 
                a.description AS description, 
                a.link AS link, 
                a.pub_date as pub_date, 
                c.link AS channel_link, 
                COUNT(l.id) AS likes
            FROM article AS a
            JOIN channel AS c ON c.id = a.channel_id 
            LEFT JOIN likes as l ON a.id = l.article_id
            WHERE a.uuid = %s
            GROUP BY a.id, c.link
        """
        params = (uuid,)

        db_result = self._execute(query, params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_article"
            )

        if not db_result.data:
            return None

        try:
            return Article(**db_result.data[0])
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_article")

    def article_uuid_to_id(self, article_uuid: str) -> Optional[int]:
        query = "SELECT id FROM article WHERE uuid = %s"
        db_result = self._execute(query, (article_uuid,))

        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="article_uuid_to_id"
            )

        if not db_result.data:
            return None

        try:
            return db_result.data[0]["id"]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="article_uuid_to_id")

    def like_article(self, article_id: int, consumer_id: int) -> bool:
        query = """
            SELECT 1 FROM likes where article_id = %s AND consumer_id = %s
        """
        params = (article_id, consumer_id,)
        db_result = self._execute(query, params)
        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="like_article"
            )

        if not db_result.data:
            query = "INSERT INTO likes(article_id, consumer_id) VALUES (%s, %s)"
            liked = True
        else:
            query = "DELETE FROM likes WHERE article_id = %s AND consumer_id = %s"
            liked = False

        db_result = self._execute(query, params)

        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="like_article"
            )

        if not db_result.row_count > 0:
            raise DatabaseError(
                message="No rows were changed when liking an article.",
                method="like_article"
            )

        return liked

    def get_unthemed_articles(self, hours: int) -> list[Article]:
        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        sql = """
            SELECT a.id AS id, 
            a.uuid as uuid, 
            a.title as title, 
            a.description as description, 
            a.link as link, 
            a.pub_date as pub_date, 
            a.embedding as embedding,
            c.link as channel_link,
            c.logo_url as channel_logo,
            COUNT(l.id) AS likes
            FROM article AS a 
            JOIN channel AS c ON c.id = a.channel_id 
            LEFT JOIN likes AS l ON l.article_id = a.id
            WHERE a.pub_date >= %s AND a.theme_id IS NULL
            GROUP BY a.id, c.link
        """

        params = (since_date,)
        result = self._execute(sql, params)

        if not result.success:
            raise DatabaseError(
                message=result.error_message if result.error_message else "Unknown error",
                method="get_unthemed_articles"
            )

        try:
            return [Article(**row) for row in (result.data if result.data else [])]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_unthemed_articles")

    def save_articles_unthemed(self, articles: list[ArticleWithChannelID]) -> list[ArticleSearchEntry]:
        if not articles:
            return []

        sql = """
            INSERT INTO article (uuid, title, description, link, pub_date, embedding, channel_id) VALUES
        """ + ", ".join([
            "(%s, %s, %s, %s, %s, %s, %s)" for _ in range(len(articles))
        ]) + """
            RETURNING id, title, description, pub_date, channel_id
        """

        params = []
        for article in articles:
            params.extend([article.uuid, article.title, article.description, article.link, article.pub_date, article.embedding, article.channel_id])

        result = self._execute(sql, tuple(params))

        if not result.success:
            raise DatabaseError(
                message=result.error_message if result.error_message else "Unknown error",
                method="save_articles_unthemed"
            )

        return [ArticleSearchEntry(**row) for row in result.data] if result.data else []