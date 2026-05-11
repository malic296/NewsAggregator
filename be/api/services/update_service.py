import json
from dataclasses import asdict
from api.interfaces import ElasticSearchInterface, ArticleInterface, ChannelInterface, ThemesInterface
from api.services import SemanticService
from api.models import ThemeCandidates, ArticleWithChannelID

class UpdateService:
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

        new_articles_unthemed: list[ArticleWithChannelID] = []
        new_articles_themed: list[ArticleWithChannelID] = []
        themes = self.themes.get_all_themes_without_articles(hours=hours)

        for channel_id, articles in new_data:
            for article in articles:
                if not article.embedding:
                    normalized_text = self.semantics.normalize_text(article.title + " " + article.description)
                    article.embedding = self.semantics.create_embedding(normalized_text)

                for theme in themes:
                    if self.semantics.get_similarity_percentage(article.embedding, theme.centroid) > 75:
                        article.theme_id = theme.id
                        break

                article_with_channel_id = ArticleWithChannelID(**asdict(article))
                article_with_channel_id.channel_id = channel_id

                if article_with_channel_id.theme_id:
                    new_articles_themed.append(article_with_channel_id)
                else:
                    new_articles_unthemed.append(article_with_channel_id)

        candidates: list[ThemeCandidates] = []
        for article in new_articles_unthemed:
            placed = False
            for candidate in candidates:
                for grouped_article in candidate.new_articles:
                    if self.semantics.get_similarity_percentage(grouped_article.embedding, article.embedding) > 75:
                        candidate.new_articles.append(article)
                        placed = True
                        break

                if placed:
                    break

            if not placed:
                candidates.append(ThemeCandidates(new_articles = [article], unthemed_articles = []))

        unthemed_articles = self.articles.get_unthemed_articles(hours=hours)

        for unthemed_article in unthemed_articles:
            unthemed_article_matched = False
            for candidate in candidates:
                for new_article in candidate.new_articles:
                    if self.semantics.get_similarity_percentage(new_article.embedding, unthemed_article.embedding) > 75:
                        candidate.unthemed_articles.append(unthemed_article)
                        unthemed_article_matched = True
                        break

                if unthemed_article_matched:
                    break

        # save new articles to existing themes and update themes centroid
        matched_with_existing_theme_entries = self.themes.add_articles_to_existing_themes(new_themed_articles=new_articles_themed)

        clusters: list[ThemeCandidates] = []
        unmatched: list[ArticleWithChannelID] = []

        # Filter candidates to clusters or unmatched articles
        for candidate in candidates:
            if len(candidate.new_articles) == 1 and len(candidate.unthemed_articles) == 0:
                unmatched.append(candidate.new_articles[0])
            else:
                embeddings = [
                    json.loads(article.embedding) if isinstance(article.embedding, str) else article.embedding
                    for article in (candidate.new_articles + candidate.unthemed_articles)
                ]
                candidate.centroid = self.semantics.calculate_centroid_embedding(embeddings)
                clusters.append(candidate)

        matched_with_unthemed_entries = self.themes.save_candidates_to_new_themes(candidates=clusters)

        unmatched_entries = self.articles.save_articles_unthemed(articles=unmatched)

        self.elasticsearch.save_article_entries(matched_with_existing_theme_entries + matched_with_unthemed_entries + unmatched_entries)




