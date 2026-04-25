import uuid
import xml.etree.ElementTree as ET
from .feed_parser import FeedParser
from app.core.errors import ScrapingError
from datetime import datetime, timedelta, timezone
from app.models.scraped_data import ScrapedChannel
from app.models import Article
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class AtomParser(FeedParser):
    def __init__(self):
        self.namespace = "{http://www.w3.org/2005/Atom}"

    def can_parse(self, root: ET.Element) -> bool:
        return root.tag == f"{self.namespace}feed"

    def parse(self, root: ET.Element, hours: int = 1) -> Optional[ScrapedChannel]:
        channel_title = root.findtext(f"{self.namespace}title", None)
        link_elem = root.find(f"{self.namespace}link[@rel='alternate']")
        channel_link = link_elem.attrib.get("href", "") if link_elem is not None else None
        image_element = root.find(f"{self.namespace}image")
        logo_elem = image_element.find(f"{self.namespace}url") if image_element is not None else None
        channel_logo = logo_elem.text if logo_elem is not None else None

        if not channel_link or not channel_title or not channel_logo:
            logger.info(f"Atom parser failed to parse the RSS feed because (title, link, logo): {channel_title}, {channel_link}, {channel_logo}")
            return None

        result = ScrapedChannel(
            title=channel_title.strip(),
            link=channel_link.strip(),
            uuid=str(uuid.uuid4()),
            logo_url=channel_logo,
            articles=[]
        )

        entries = root.findall(f"{self.namespace}entry")
        for e in entries:
            try:
                e_pub_date = e.findtext(f"{self.namespace}published") or e.findtext(f"{self.namespace}updated")
                e_pub_date = self._parse_str_to_date(e_pub_date)

                if e_pub_date < datetime.now(tz=timezone.utc) - timedelta(hours=hours):
                    continue

                e_link_tag = e.find(f"{self.namespace}link")
                e_link = e_link_tag.attrib.get("href", "") if e_link_tag is not None else None
                e_link = e_link.strip()

                e_title = e.findtext(f"{self.namespace}title", None).strip()
                e_desc = e.findtext(f"{self.namespace}summary", "").strip()
            except Exception as e:
                raise Exception(f"Atom parser failed to parse the Atom feed because {e}.")

            result.articles.append(
                Article(
                    title=e_title,
                    link=e_link,
                    description=e_desc,
                    pub_date=e_pub_date,
                    uuid=str(uuid.uuid4()),
                    channel_link=channel_link.strip(),
                    likes=0

                )
            )

        return result