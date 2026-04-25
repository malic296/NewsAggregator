from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ChannelDTO")


@_attrs_define
class ChannelDTO:
    """
    Attributes:
        uuid (str):
        title (str):
        link (str):
        disabled_by_user (bool):
        logo_url (str):
        feed_url (None | str | Unset):
    """

    uuid: str
    title: str
    link: str
    disabled_by_user: bool
    logo_url: str
    feed_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid = self.uuid

        title = self.title

        link = self.link

        disabled_by_user = self.disabled_by_user

        logo_url = self.logo_url

        feed_url: None | str | Unset
        if isinstance(self.feed_url, Unset):
            feed_url = UNSET
        else:
            feed_url = self.feed_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "uuid": uuid,
                "title": title,
                "link": link,
                "disabled_by_user": disabled_by_user,
                "logo_url": logo_url,
            }
        )
        if feed_url is not UNSET:
            field_dict["feed_url"] = feed_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        uuid = d.pop("uuid")

        title = d.pop("title")

        link = d.pop("link")

        disabled_by_user = d.pop("disabled_by_user")

        logo_url = d.pop("logo_url")

        def _parse_feed_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        feed_url = _parse_feed_url(d.pop("feed_url", UNSET))

        channel_dto = cls(
            uuid=uuid,
            title=title,
            link=link,
            disabled_by_user=disabled_by_user,
            logo_url=logo_url,
            feed_url=feed_url,
        )

        channel_dto.additional_properties = d
        return channel_dto

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
