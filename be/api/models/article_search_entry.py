from dataclasses import dataclass
from datetime import datetime

@dataclass
class ArticleSearchEntry:
    id: int
    title: str
    description: str
    pub_date: datetime
    channel_id: int