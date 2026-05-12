from pydantic import BaseModel
from api.models.enums import OrderByEnum

class OrderBy(BaseModel):
    field: OrderByEnum