import uuid
from api.models import Article, ArticleSearchEntry, Theme

class UpdateService:
    EXISTING_THEME_MATCH_THRESHOLD = 75.0
    NEW_THEME_MATCH_THRESHOLD = 80.0

    def __init__(self, scraping_service, themes, articles, channels, elasticsearch, semantics):
        self.scraping_service = scraping_service
        self.themes = themes
        self.articles = articles
        self.channels = channels
        self.elasticsearch = elasticsearch
        self.semantics = semantics

    async def update_data(self, channel_urls: list[str], hours: int) -> None:
        channels = await self.scraping_service.fetch_channels(feeds=channel_urls, hours=hours)
        new_data = self.channels.get_new_articles(channels)

        if not new_data:
            return

        all_new_articles: list[Article] = []
        chan_id_map = {}
        for c_id, articles in new_data:
            for a in articles:
                chan_id_map[a.channel_link] = c_id
                all_new_articles.append(a)

        for art in all_new_articles:
            text = self.semantics.normalize_text(f"{art.title} {art.description}")
            art.embedding = self.semantics.create_embedding(text)

        existing_themes = self.themes.read_themes(72)
        for art in all_new_articles:
            for theme in existing_themes:
                sims = [self.semantics.get_similarity_percentage(art.embedding, ta.embedding)
                        for ta in theme.articles]

                if sims and (sum(sims) / len(sims)) >= self.EXISTING_THEME_MATCH_THRESHOLD:
                    art.theme_id = theme.id
                    break

        themeless = [a for a in all_new_articles if a.theme_id is None]
        discovered_themes = self._discover_new_themes(themeless)

        if discovered_themes:
            uuid_map = self.themes.create_themes_bulk(discovered_themes)
            for theme in discovered_themes:
                real_db_id = uuid_map[theme.uuid]
                for art in theme.articles:
                    art.theme_id = real_db_id

        saved_rows = self.articles.bulk_save_articles(all_new_articles, chan_id_map)

        if saved_rows:
            search_entries = [ArticleSearchEntry(**row) for row in saved_rows]
            self.elasticsearch.save_article_entries(search_entries)
            self.elasticsearch.delete_old_articles(72)

    def _discover_new_themes(self, articles: list[Article]) -> list[Theme]:
        new_themes = []
        processed_indices = set()

        for i, art_a in enumerate(articles):
            if i in processed_indices: continue

            cluster = [art_a]
            for j, art_b in enumerate(articles):
                if i == j or j in processed_indices: continue

                if self.semantics.get_similarity_percentage(art_a.embedding, art_b.embedding) >= self.NEW_THEME_MATCH_THRESHOLD:
                    cluster.append(art_b)

            if len(cluster) >= 2:
                new_themes.append(Theme(
                    uuid=str(uuid.uuid4()),
                    newest_date=max(a.pub_date for a in cluster),
                    articles=cluster
                ))
                for clustered_art in cluster:
                    processed_indices.add(articles.index(clustered_art))

        return new_themes
