import xml.etree.ElementTree as ET
from app.core.errors import ScrapingError
from .feed_parser import FeedParser
from datetime import datetime, timedelta, timezone
from app.models.scraped_data import ScrapedChannel
from app.models import Channel, Article
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
        channel_logo = channel.findtext("image/url", default=None)

        atom_ns = {"atom": "http://www.w3.org/2005/Atom"}
        atom_link_elem = channel.find("atom:link[@rel='self']", atom_ns)
        feed_url = atom_link_elem.attrib.get("href") if atom_link_elem is not None else None

        if not channel_link or not channel_link or not channel_logo:
            logger.info(f"RSS parser failed to parse the RSS feed because (title, link, logo): {channel_title}, {channel_link}, {channel_logo}")
            return None

        result = ScrapedChannel(
            title=channel_title.strip(),
            link=channel_link.strip(),
            feed_url=feed_url,
            uuid=str(uuid.uuid4()),
            logo_url=channel_logo.strip(),
            articles=[]
        )

        items = channel.findall("item")
        for item in items:
            try:
                i_pubdate = item.findtext("pubDate", default=None).strip()
                parsed_pubdate = self._parse_str_to_date(i_pubdate)

                if parsed_pubdate < datetime.now(tz=timezone.utc) - timedelta(hours=hours):
                    continue

                i_title = item.findtext("title", default=None).strip()
                i_link = item.findtext("link", default=None).strip()
                i_description = item.findtext("description", default="").strip()

            except Exception as e:
                raise Exception(f"RSS parser failed to parse the RSS feed because {e}.")

            result.articles.append(
                Article(
                    title=i_title,
                    link=i_link,
                    description=i_description,
                    pub_date=parsed_pubdate,
                    uuid=str(uuid.uuid4()),
                    channel_link=channel_link.strip(),
                    likes=0

                )
            )

        return result