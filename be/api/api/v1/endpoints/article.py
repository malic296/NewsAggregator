from fastapi import Depends, APIRouter, Query
from api.models import Article, Consumer
from api.schemas.responses import ArticlesResponse, ArticleResponse, LikeResponse
from api.api.dependencies import get_article_service, get_current_user
from dataclasses import asdict
from api.schemas import ArticleDTO, PagedArticlesDTO
from api.models.paged_articles import PagedArticles

article_router = APIRouter(
    prefix = "/articles",
    tags = ["articles"]
)

@article_router.get("/", response_model=PagedArticlesDTO)
def articles(hours: int = 1, order_by_likes: bool = True, cursor: str | None = Query(None), page: int | None = Query(None), query: str | None = Query(None), user = Depends(get_current_user), article_service = Depends(get_article_service)):
    paged_result: PagedArticles = article_service.get_articles(consumer=user, hours=hours, order_by_likes=order_by_likes, cursor = cursor, query=query, page=page)
    
    return PagedArticlesDTO(
        articles=[ArticleDTO(**asdict(article)) for article in paged_result.articles],
        next_cursor=paged_result.next_cursor,
        has_more=paged_result.has_more
    )

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

