from elasticsearch import Elasticsearch
from api.interfaces import ElasticSearchInterface
from api.models import ArticleSearchEntry
import logging
from api.core.errors import ElasticSearchError
from elasticsearch.helpers import bulk
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class ElasticSearchRepository(ElasticSearchInterface):
    def __init__(self, client: Elasticsearch):
        self._client = client
        self._INDEX = "articles"
        self.PAGE_SIZE = 10

    def save_article_entries(self, entries: list[ArticleSearchEntry]) -> None:
        if not entries or len(entries) == 0:
            logger.info("No new entries to save to elastic search.")
            return

        logger.info(f"Saving {len(entries)} new entries to elastic search.")

        try:
            actions = [
                {
                    "_index": self._INDEX,
                    "_id": entry.id,
                    "_source": {
                        "id": entry.id,
                        "title": entry.title,
                        "description": entry.description,
                        "pub_date": entry.pub_date.isoformat()
                    }

                }
                for entry in entries
            ]

            bulk(self._client, actions)
        except Exception as e:
            raise ElasticSearchError(message=str(e), method="save_article_entries")


    def delete_old_articles(self, hours: int) -> None:
        breakpoint_date = (datetime.now() - timedelta(hours=hours)).isoformat()
        query = {
            "query": {
                "range": {
                    "pub_date": {
                        "lt": breakpoint_date
                    }
                }
            }
        }
        try:
            self._client.delete_by_query(index=self._INDEX, body=query)
        except Exception as e:
            raise ElasticSearchError(message=str(e), method="delete_old_articles")

    def search_articles(self, query: str, hours: int, disabled_channel_ids: list[int], page: int = 1) -> tuple[list[int], bool]:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        offset = (page - 1) * self.PAGE_SIZE

        results = self._client.search(
            index=self._INDEX,
            body={
                "from": offset,
                "size": self.PAGE_SIZE + 1,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["title^2", "description"]
                                }
                            }
                        ],
                        "filter": [
                            {"range": {"pub_date": {"gte": cutoff}}}
                        ],
                        "must_not": [
                            {"terms": {"channel_id": disabled_channel_ids}}
                        ] if disabled_channel_ids else []
                    }
                }

            }
        )

        hits = results["hits"]["hits"]
        has_more = len(hits) > self.PAGE_SIZE
        hits = hits[:self.PAGE_SIZE]

        ids = [hit["_source"]["id"] for hit in hits]
        return ids, has_more