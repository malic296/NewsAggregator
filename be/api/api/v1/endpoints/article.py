from fastapi import Depends, APIRouter, Query
from api.models import Article, Consumer
from api.schemas.responses import ArticleResponse, LikeResponse
from api.api.dependencies import get_article_service, get_current_user
from dataclasses import asdict
from api.schemas import ArticleDTO, PagedArticlesDTO, OrderBy

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/", response_model=PagedArticlesDTO)
def articles(order_by: OrderBy, hours: int = 1, cursor: str | None = Query(None), page: int | None = Query(None), query: str | None = Query(None), user = Depends(get_current_user), article_service = Depends(get_article_service)):
    return article_service.get_articles(consumer=user, hours=hours, order_by=order_by.field, cursor = cursor, query=query, page=page)

@article_router.get("/{uuid}", response_model=ArticleResponse)
def article(uuid: str, article_service = Depends(get_article_service)):
    article: Article = article_service.get_article(uuid)

    return ArticleResponse(
        message="Article fetched correctly",
        success=True,
        article=ArticleDTO(**asdict(article))
    )

@article_router.post("/{article_uuid}/like", response_model=LikeResponse)
def like(article_uuid: str, user: Consumer = Depends(get_current_user), article_service = Depends(get_article_service)):
    liked: bool = article_service.like_article(article_uuid, user)
    return LikeResponse(
        success= True,
        message = f"Article with uuid {article_uuid} has been liked." if liked else f"Article with uuid {article_uuid} has been unliked.",
        liked=liked
    )

