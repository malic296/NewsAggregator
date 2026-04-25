from pydantic import BaseModel
from typing import Optional

class ChannelDTO(BaseModel):
    uuid: str
    title: str
    link: str
    disabled_by_user: bool
    logo_url: str
    feed_url: Optional[str] = None
