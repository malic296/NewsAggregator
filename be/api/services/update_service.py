from api.interfaces import ElasticSearchInterface, ArticleInterface, ChannelInterface, ThemesInterface
from api.services import SemanticService
class UpdateService:
    EXISTING_THEME_MATCH_THRESHOLD = 75.0
    NEW_THEME_MATCH_THRESHOLD = 80.0

    def __init__(self, scraping_service, themes: ThemesInterface, articles: ArticleInterface, channels: ChannelInterface, elasticsearch: ElasticSearchInterface, semantics: SemanticService):
        self.scraping_service = scraping_service
        self.themes = themes
        self.articles = articles
        self.channels = channels
        self.elasticsearch = elasticsearch
        self.semantics = semantics

    async def update_data(self, channel_urls: list[str], hours: int) -> None:
        channels = await self.scraping_service.fetch_channels(feeds=channel_urls, hours=hours)
        new_data = self.channels.get_new_articles(channels)

        channel_id_map = {}
        new_articles = []
        for channel_id, articles in new_data:
            for article in articles:
                if article.embedding is None:
                    normalized_text = self.semantics.normalize_text(article.title + " " + article.description)
                    article.embedding = self.semantics.create_embedding(normalized_text)

                channel_id_map[article.channel_link] = channel_id

            new_articles.extend(articles)

        es_entries_to_save = self.articles.bulk_save_articles(new_articles, channel_id_map=channel_id_map)
        self.elasticsearch.save_article_entries(es_entries_to_save)

        self.articles.assign_new_themes(hours_limit=72)




