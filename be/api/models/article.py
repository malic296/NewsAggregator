from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    uuid: str
    title: str
    link: str
    description: str
    pub_date: datetime
    channel_link: str
    channel_logo: str
    likes: int = -1
    liked_by_user: bool = False
    id: Optional[int] = None
    embedding: Optional[list[float]] = None
    theme_id: Optional[int] = None