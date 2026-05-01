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
    likes: int
    channel_logo: Optional[str] = None
    liked_by_user: bool = False
    id: Optional[int] = None
    embedding: Optional[list[float]] = None