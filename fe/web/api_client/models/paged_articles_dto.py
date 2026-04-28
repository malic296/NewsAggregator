from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.article_dto import ArticleDTO


T = TypeVar("T", bound="PagedArticlesDTO")


@_attrs_define
class PagedArticlesDTO:
    """
    Attributes:
        articles (list[ArticleDTO]):
        next_cursor (None | str | Unset):
        next_page (int | None | Unset):
        has_more (bool | Unset):  Default: False.
    """

    articles: list[ArticleDTO]
    next_cursor: None | str | Unset = UNSET
    next_page: int | None | Unset = UNSET
    has_more: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        articles = []
        for articles_item_data in self.articles:
            articles_item = articles_item_data.to_dict()
            articles.append(articles_item)

        next_cursor: None | str | Unset
        if isinstance(self.next_cursor, Unset):
            next_cursor = UNSET
        else:
            next_cursor = self.next_cursor

        next_page: int | None | Unset
        if isinstance(self.next_page, Unset):
            next_page = UNSET
        else:
            next_page = self.next_page

        has_more = self.has_more

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "articles": articles,
            }
        )
        if next_cursor is not UNSET:
            field_dict["next_cursor"] = next_cursor
        if next_page is not UNSET:
            field_dict["next_page"] = next_page
        if has_more is not UNSET:
            field_dict["has_more"] = has_more

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.article_dto import ArticleDTO

        d = dict(src_dict)
        articles = []
        _articles = d.pop("articles")
        for articles_item_data in _articles:
            articles_item = ArticleDTO.from_dict(articles_item_data)

            articles.append(articles_item)

        def _parse_next_cursor(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        next_cursor = _parse_next_cursor(d.pop("next_cursor", UNSET))

        def _parse_next_page(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        next_page = _parse_next_page(d.pop("next_page", UNSET))

        has_more = d.pop("has_more", UNSET)

        paged_articles_dto = cls(
            articles=articles,
            next_cursor=next_cursor,
            next_page=next_page,
            has_more=has_more,
        )

        paged_articles_dto.additional_properties = d
        return paged_articles_dto

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
