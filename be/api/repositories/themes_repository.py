from datetime import datetime, timedelta, timezone
from api.core.errors import DatabaseError, MappingError
from api.interfaces import ThemesInterface
from api.models import Theme, Article, PagedThemes, ArticleWithChannelID, ArticleSearchEntry, ThemeCandidates
from api.repositories.base_repository import BaseRepository
import uuid

class ThemesRepository(ThemesInterface, BaseRepository):
    def read_themes(self, consumer_id: int, sort_value: str | None, uuid: str | None, hours: int = 72) -> list[Theme]:
        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        params = [since_date]

        cursor_filter = "TRUE"
        if sort_value and uuid:
            cursor_dt = datetime.fromisoformat(sort_value) if isinstance(sort_value, str) else sort_value
            cursor_filter = f"newest_date < %s OR (newest_date = %s AND uuid < %s)"
            params.extend([cursor_dt, cursor_dt, uuid])

        params.append(self.PAGE_SIZE + 1)

        query = f"""
            WITH target_themes AS (
                SELECT id, uuid, newest_date
                FROM theme
                WHERE newest_date >= %s
                AND {cursor_filter}
                ORDER BY newest_date DESC, uuid DESC
                LIMIT %s
            )
            SELECT 
                t.id AS theme_id, t.uuid AS theme_uuid, t.newest_date AS theme_newest_date,
                a.id AS article_id, a.uuid as article_uuid, a.title as article_title, a.description as article_description, a.link as article_link, a.pub_date as article_pub_date, a.embedding AS article_embedding,
                c.link as channel_link, c.logo_url as channel_logo,
                COUNT(l.id) OVER (PARTITION BY a.id) AS likes,
                EXISTS(
                    SELECT 1 FROM likes
                    WHERE article_id = a.id AND consumer_id = %s
                ) AS liked_by_user
            FROM target_themes AS t 
            JOIN article AS a ON a.theme_id = t.id
            JOIN channel AS c ON c.id = a.channel_id
            LEFT JOIN likes as l ON a.id = l.article_id
            ORDER BY t.newest_date DESC, t.uuid DESC, a.pub_date DESC
        """

        result = self._execute(query=query, params=tuple(params + [consumer_id]))
        if not result.success:
            raise DatabaseError(
                message=result.error_message if result.error_message else "Unknown error",
                method="read_themes"
            )

        theme_map = {}

        for row in result.data:
            if row["theme_id"] not in theme_map:
                theme_map[row["theme_id"]] = Theme(id=row["theme_id"], uuid=row["theme_uuid"], newest_date=row["theme_newest_date"], articles = [])

            theme_map[row["theme_id"]].articles.append(
                Article(
                    id=row["article_id"],
                    uuid=row["article_uuid"],
                    title=row["article_title"],
                    description=row["article_description"],
                    link=row["article_link"],
                    pub_date=row["article_pub_date"],
                    embedding=row["article_embedding"],
                    channel_logo=row["channel_logo"],
                    channel_link=row["channel_link"],
                    likes=row["likes"],
                    liked_by_user=row["liked_by_user"]
                )
            )

        return list(theme_map.values())

    def get_all_themes_without_articles(self, hours: int) -> list[Theme]:
        since_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        sql = """
            SELECT 
                t.id AS id, 
                t.uuid AS uuid, 
                t.newest_date AS newest_date, 
                t.centroid_embedding AS centroid
            FROM theme AS t
            WHERE t.newest_date >= %s
        """

        result = self._execute(sql, (since_date,))
        if not result.success:
            raise DatabaseError(
                message=result.error_message if result.error_message else "Unknown error",
                method="get_all_themes"
            )

        return [Theme(**row) for row in result.data] if result.data else []

    def add_articles_to_existing_themes(self, new_themed_articles: list[ArticleWithChannelID]) -> list[ArticleSearchEntry]:
        if not new_themed_articles:
            return []

        insert_sql = """
            WITH inserted AS (
                INSERT INTO article (uuid, title, description, link, pub_date, embedding, channel_id, theme_id)
                VALUES 
                """ + ", ".join([
                    "(%s, %s, %s, %s, %s, %s, %s, %s)"
                    for _ in new_themed_articles
                ]) + """
                RETURNING id, title, description, pub_date, channel_id, theme_id, embedding
            ),
            updated AS (
                UPDATE theme AS t
                SET centroid_embedding = sub.avg_embedding
                FROM (
                    SELECT theme_id, AVG(embedding) AS avg_embedding
                    FROM inserted 
                    GROUP BY theme_id
                ) AS sub
                WHERE t.id = sub.theme_id
            )
            SELECT * FROM inserted;
        """

        params = []
        for article in new_themed_articles:
            params.extend([
                article.uuid,
                article.title,
                article.description,
                article.link,
                article.pub_date,
                article.embedding,
                article.channel_id,
                article.theme_id,
            ])

        result = self._execute(insert_sql, tuple(params))

        if not result.success:
            raise DatabaseError(
                message=result.error_message if result.error_message else "Unknown error",
                method="add_articles_to_existing_theme"
            )

        try:
            return [ArticleSearchEntry(id=row["id"], title=row["title"], description=row["description"], pub_date=row["pub_date"], channel_id=row["channel_id"]) for row in result.data] if result.data else []
        except Exception as e:
            raise MappingError(mapping_error=str(e), method="add_articles_to_existing_theme")

    def save_candidates_to_new_themes(self, candidates: list[ThemeCandidates]) -> list[ArticleSearchEntry]:
        result: list[ArticleSearchEntry] = []
        for candidate in candidates:
            newest_date: datetime = max((a.pub_date for a in candidate.new_articles + candidate.unthemed_articles), default=datetime.now(timezone.utc))
            theme_uuid = str(uuid.uuid4())

            theme_sql = f"""
                INSERT INTO theme (uuid, newest_date, centroid_embedding) 
                VALUES (%s, %s, %s) 
                RETURNING id
            """

            theme_params = (theme_uuid, newest_date, candidate.centroid)

            theme_result = self._execute(theme_sql, theme_params)
            if not theme_result.success:
                raise DatabaseError(
                    message=theme_result.error_message if theme_result.error_message else "Unknown error",
                    method="save_candidates_to_new_themes"
                )

            try:
                theme_id: int = theme_result.data[0]["id"]
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="save_candidates_to_new_themes")

            transactions = []

            for a in candidate.new_articles:
                transactions.append(
                    (
                        "INSERT INTO article(uuid, title, link, description, pub_date, channel_id, embedding, theme_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id, title, description, pub_date, channel_id",
                        (str(uuid.uuid4()), a.title, a.link, a.description, a.pub_date, a.channel_id, a.embedding, theme_id)
                     )
                )

            for a in candidate.unthemed_articles:
                transactions.append(
                    (
                        "UPDATE article SET theme_id = %s WHERE id = %s",
                        (theme_id, a.id)
                    )
                )

            bulk_result = self._execute_transaction_returning(transactions)

            if not bulk_result.success:
                delete_ghost_theme = f"DELETE FROM theme WHERE id = %s"
                delete_theme_result = self._execute(delete_ghost_theme, (theme_id,))

                if not delete_theme_result.success:
                    raise DatabaseError(
                        message=delete_theme_result.error_message + " This fail happened after bulk insert failed while trying to delete the new ghost theme." if delete_theme_result.error_message else "Unknown error",
                        method="save_candidates_to_new_themes"
                    )

                raise DatabaseError(
                    message=bulk_result.error_message if bulk_result.error_message else "Unknown error",
                    method="save_candidates_to_new_themes"
                )

            try:
                new_entries = [ArticleSearchEntry(id=row["id"], title=row["title"], description=row["description"], pub_date=row["pub_date"], channel_id=row["channel_id"]) for row in bulk_result.data] if bulk_result.data else []
                result.extend(new_entries)
            except Exception as e:
                raise MappingError(mapping_error=str(e), method="save_candidates_to_new_themes")

        return result
