from dataclasses import dataclass
from .article import Article
from .channel import Channel

@dataclass
class ScrapedChannel:
    title: str
    link: str
    feed_url: str
    uuid: str
    logo_url: str
    articles: list[Article]