import logging
from typing import List
from app.models.scraped_data import ScrapedChannel
import xml.etree.ElementTree as ET
from app.core.errors import ScrapingError
from httpx import AsyncClient
from asyncio import Semaphore
import asyncio
from app.parsers import AtomParser, RSSParser
import logging

logger = logging.getLogger(__name__)

class ScrapingService:
    def __init__(self, client: AsyncClient):
        self._semaphore = Semaphore(50)
        self.client = client
        self.parsers = [AtomParser(), RSSParser()]

    async def fetch_channels(self, feeds: List[str], hours: int = 1) -> list[ScrapedChannel]:
        tasks = [self._read_data_from_url(feed, hours) for feed in feeds]
        channels = await asyncio.gather(*tasks)

        return [channel for channel in channels if channel is not None]

    async def _read_data_from_url(self, link: str, hours: int = 1) -> ScrapedChannel:
        async with self._semaphore:
            try:
                content = await self._get_content_from_url(link)
            except ScrapingError as e:
                logger.error(str(e))
                return None

            try:
                xml = ET.fromstring(content)
            except ET.ParseError as e:
                logger.error(f"Failed to parse XML for {link}: {e}")
                return None

            channel = None
            for parser in self.parsers:
                if parser.can_parse(xml):
                    channel = parser.parse(xml, hours)

            return channel

    async def _get_content_from_url(self, url: str):
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            content = response.content.strip()
            return content
        except Exception as e:
            raise ScrapingError(f"HTTP Request failed for {url}: {e}")
