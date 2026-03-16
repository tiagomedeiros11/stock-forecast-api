from pydantic import BaseModel, Field
from datetime import date, datetime


class SaleCreate(BaseModel):
    quantity: float = Field(..., gt=0, example=10.0)
    date: date = Field(..., example="2024-01-15")


class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: float
    date: date
    created_at: datetime

    model_config = {"from_attributes": True}


class SaleBulkCreate(BaseModel):
    sales: list[SaleCreate] = Field(..., min_length=1)
