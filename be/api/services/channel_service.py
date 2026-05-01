from api.models import Channel, ArticleSearchEntry, Article
from api.schemas import ChannelDTO
from api.interfaces import ChannelInterface
from api.interfaces import ElasticSearchInterface, ValkeyInterface
from api.models.scraped_data import ScrapedChannel
from .scraping_service import ScrapingService
from .semantic_service import SemanticService
from api.core.errors import DependencyUnavailableError

class ChannelService:
    def __init__(self, channels: ChannelInterface, valkey: ValkeyInterface, elasticsearch: ElasticSearchInterface, semantics: SemanticService | None = None, scraping_service: ScrapingService | None = None):
        self.channels = channels
        self.valkey = valkey
        self.scraping_service = scraping_service
        self.elasticsearch = elasticsearch
        self.semantics = semantics

    def get_channels(self, user_id: int) -> list[Channel]:
        cached_channels = self.valkey.get_available_channels(user_id=user_id)
        if cached_channels:
            return cached_channels

        channels = self.channels.get_channels(user_id)
        self.valkey.set_available_channels(channels=channels, user_id=user_id)
        return channels

    def set_disabled_channels(self, user_id: int, disabled_channels: list[ChannelDTO]) -> None:
        self.valkey.invalidate_cache_channels(user_id=user_id)
        self.channels.set_disabled_channels_by_uuids(user_id, [channel.uuid for channel in disabled_channels])

    async def update_data(self, channel_urls: list[str], hours: int) -> None:
        if not self.scraping_service:
            raise DependencyUnavailableError(dependency="ScrapingService")
        channels: list[ScrapedChannel] = await self.scraping_service.fetch_channels(feeds=channel_urls, hours=hours)



        #new_entries: list[ArticleSearchEntry] = self.channels.update_channels(channels)
        #self.elasticsearch.save_article_entries(new_entries)
        #self.elasticsearch.delete_old_articles(72)


