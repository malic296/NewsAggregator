from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.paged_articles_dto import PagedArticlesDTO
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    hours: int | Unset = 1,
    order_by_likes: bool | Unset = True,
    cursor: None | str | Unset = UNSET,
    page: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["hours"] = hours

    params["order_by_likes"] = order_by_likes

    json_cursor: None | str | Unset
    if isinstance(cursor, Unset):
        json_cursor = UNSET
    else:
        json_cursor = cursor
    params["cursor"] = json_cursor

    json_page: int | None | Unset
    if isinstance(page, Unset):
        json_page = UNSET
    else:
        json_page = page
    params["page"] = json_page

    json_query: None | str | Unset
    if isinstance(query, Unset):
        json_query = UNSET
    else:
        json_query = query
    params["query"] = json_query

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/v1/articles/",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> HTTPValidationError | PagedArticlesDTO | None:
    if response.status_code == 200:
        response_200 = PagedArticlesDTO.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[HTTPValidationError | PagedArticlesDTO]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient,
    hours: int | Unset = 1,
    order_by_likes: bool | Unset = True,
    cursor: None | str | Unset = UNSET,
    page: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | PagedArticlesDTO]:
    """Articles

    Args:
        hours (int | Unset):  Default: 1.
        order_by_likes (bool | Unset):  Default: True.
        cursor (None | str | Unset):
        page (int | None | Unset):
        query (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PagedArticlesDTO]
    """

    kwargs = _get_kwargs(
        hours=hours,
        order_by_likes=order_by_likes,
        cursor=cursor,
        page=page,
        query=query,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient,
    hours: int | Unset = 1,
    order_by_likes: bool | Unset = True,
    cursor: None | str | Unset = UNSET,
    page: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
) -> HTTPValidationError | PagedArticlesDTO | None:
    """Articles

    Args:
        hours (int | Unset):  Default: 1.
        order_by_likes (bool | Unset):  Default: True.
        cursor (None | str | Unset):
        page (int | None | Unset):
        query (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PagedArticlesDTO
    """

    return sync_detailed(
        client=client,
        hours=hours,
        order_by_likes=order_by_likes,
        cursor=cursor,
        page=page,
        query=query,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient,
    hours: int | Unset = 1,
    order_by_likes: bool | Unset = True,
    cursor: None | str | Unset = UNSET,
    page: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
) -> Response[HTTPValidationError | PagedArticlesDTO]:
    """Articles

    Args:
        hours (int | Unset):  Default: 1.
        order_by_likes (bool | Unset):  Default: True.
        cursor (None | str | Unset):
        page (int | None | Unset):
        query (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[HTTPValidationError | PagedArticlesDTO]
    """

    kwargs = _get_kwargs(
        hours=hours,
        order_by_likes=order_by_likes,
        cursor=cursor,
        page=page,
        query=query,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient,
    hours: int | Unset = 1,
    order_by_likes: bool | Unset = True,
    cursor: None | str | Unset = UNSET,
    page: int | None | Unset = UNSET,
    query: None | str | Unset = UNSET,
) -> HTTPValidationError | PagedArticlesDTO | None:
    """Articles

    Args:
        hours (int | Unset):  Default: 1.
        order_by_likes (bool | Unset):  Default: True.
        cursor (None | str | Unset):
        page (int | None | Unset):
        query (None | str | Unset):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        HTTPValidationError | PagedArticlesDTO
    """

    return (
        await asyncio_detailed(
            client=client,
            hours=hours,
            order_by_likes=order_by_likes,
            cursor=cursor,
            page=page,
            query=query,
        )
    ).parsed
