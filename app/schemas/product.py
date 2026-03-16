from pydantic import BaseModel, Field
from datetime import datetime


class ProductCreate(BaseModel):
    sku: str = Field(..., example="PROD-001")
    name: str = Field(..., example="Widget A")
    current_stock: float = Field(..., ge=0, example=150.0)
    reorder_point: float = Field(..., ge=0, example=30.0)


class ProductUpdate(BaseModel):
    name: str | None = None
    current_stock: float | None = Field(None, ge=0)
    reorder_point: float | None = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    current_stock: float
    reorder_point: float
    created_at: datetime

    model_config = {"from_attributes": True}
