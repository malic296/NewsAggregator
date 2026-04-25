from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="ArticleDTO")


@_attrs_define
class ArticleDTO:
    """
    Attributes:
        uuid (str):
        title (str):
        link (str):
        description (str):
        pub_date (datetime.datetime):
        channel_link (str):
        likes (int):
        channel_logo (str):
        liked_by_user (bool | Unset):  Default: False.
    """

    uuid: str
    title: str
    link: str
    description: str
    pub_date: datetime.datetime
    channel_link: str
    likes: int
    channel_logo: str
    liked_by_user: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        title = self.title

        link = self.link

        description = self.description

        pub_date = self.pub_date.isoformat()

        channel_link = self.channel_link

        likes = self.likes

        channel_logo = self.channel_logo

        liked_by_user = self.liked_by_user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "title": title,
                "link": link,
                "description": description,
                "pub_date": pub_date,
                "channel_link": channel_link,
                "likes": likes,
                "channel_logo": channel_logo,
            }
        )
        if liked_by_user is not UNSET:
            field_dict["liked_by_user"] = liked_by_user

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = d.pop("uuid")

        title = d.pop("title")

        link = d.pop("link")

        description = d.pop("description")

        pub_date = isoparse(d.pop("pub_date"))

        channel_link = d.pop("channel_link")

        likes = d.pop("likes")

        channel_logo = d.pop("channel_logo")

        liked_by_user = d.pop("liked_by_user", UNSET)

        article_dto = cls(
            uuid=uuid,
            title=title,
            link=link,
            description=description,
            pub_date=pub_date,
            channel_link=channel_link,
            likes=likes,
            channel_logo=channel_logo,
            liked_by_user=liked_by_user,
        )

        article_dto.additional_properties = d
        return article_dto

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
