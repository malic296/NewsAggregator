from typing import Optional
from .base_repository import BaseRepository
from app.interfaces.article_interface import ArticleInterface
from datetime import datetime, timezone, timedelta
from app.models import Consumer, Article
from app.core.errors import MappingError, DatabaseError

class ArticleRepository(BaseRepository, ArticleInterface):
    def get_articles(self, consumer: Consumer, hours: int = 1) -> list[Article]:
        query = """
                SELECT 
                    a.id, a.uuid, a.title, a.description, a.link, a.pub_date, 
                    c.link AS channel_link, c.logo_url AS channel_logo, 
                    COUNT(l.id) as likes,
                    EXISTS (
                        SELECT 1 FROM likes 
                        WHERE article_id = a.id AND consumer_id = %s
                    ) AS liked_by_user    
                FROM article AS a 
                JOIN channel AS c ON c.id = a.channel_id
                LEFT JOIN likes AS l ON a.id = l.article_id
                WHERE a.pub_date >= %s
                  AND a.channel_id NOT IN (
                      SELECT channel_id FROM disabled WHERE consumer_id = %s
                  )
                GROUP BY a.id, c.link, c.logo_url
                ORDER BY a.pub_date DESC
            """

        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)

        params = (consumer.id, since_date, consumer.id)

        db_result = self._execute(query, params)

        if not db_result.success:
            raise DatabaseError(
                message=db_result.error_message if db_result.error_message else "Unknown error",
                method="get_articles"
            )

        try:
            return [Article(**article) for article in db_result.data]
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="get_articles")

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