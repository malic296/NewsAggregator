from fastapi import APIRouter, Depends, Query
from api.api.dependencies import get_themes_service
from api.api.dependencies import get_current_user
from api.schemas import PagedThemesDTO

themes_router = APIRouter(
    prefix="/themes",
    tags=["themes"]
)

@themes_router.get("/", response_model=PagedThemesDTO)
def themes(hours: int = 72, cursor: str | None = Query(None), page: int | None = Query(None), themes_service = Depends(get_themes_service), user = Depends(get_current_user)):
    return themes_service.get_themes(consumer=user, hours=hours, cursor=cursor, page=page)



