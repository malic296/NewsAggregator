import xml.etree.ElementTree as ET
from api.core.errors import ScrapingError
from .feed_parser import FeedParser
from datetime import datetime, timedelta, timezone
from api.models.scraped_data import ScrapedChannel
from api.models import Channel, Article
import uuid
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class RSSParser(FeedParser):
    def can_parse(self, root: ET.Element) -> bool:
        return root.tag == "rss"

    def parse(self, root: ET.Element, hours: int = 1) -> Optional[ScrapedChannel]:
        channel = root.find("channel")
        if channel is None:
            raise ScrapingError(f"Channel tag not found for: {root}")

        channel_title = channel.findtext("title", default=None)
        channel_link = channel.findtext("link", default=None)

        if not channel_title or not channel_link:
            logger.info(f"RSS parser failed to parse the RSS feed because (title, link): {channel_title}, {channel_link}")
            return None

        result = ScrapedChannel(
            title=channel_title.strip(),
            link=channel_link.strip(),
            uuid=str(uuid.uuid4()),
            logo_url=f"https://s2.googleusercontent.com/s2/favicons?domain={channel_link}",
            articles=[]
        )

        items = channel.findall("item")
        for item in items:
            try:

                i_pubdate = item.findtext("pubDate", default=None)
                if not i_pubdate:
                    continue
                parsed_pubdate = self._parse_str_to_date(i_pubdate.strip())

                if parsed_pubdate < datetime.now(tz=timezone.utc) - timedelta(hours=hours):
                    continue

                i_title = item.findtext("title", default=None)
                i_link = item.findtext("link", default=None)
                i_description = item.findtext("description", default=None)

                if not i_title or not i_link or not i_description:
                    continue


            except Exception as e:
                raise Exception(f"RSS parser failed to parse the RSS feed because {e}.")

            result.articles.append(
                Article(
                    title=i_title.strip(),
                    link=i_link.strip(),
                    description=i_description.strip(),
                    pub_date=parsed_pubdate,
                    uuid=str(uuid.uuid4()),
                    channel_link=channel_link.strip(),
                    likes=0,
                    channel_logo=f"https://s2.googleusercontent.com/s2/favicons?domain={channel_link}"
                )
            )

        return result