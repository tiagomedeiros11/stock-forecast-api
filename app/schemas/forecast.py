from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Confidence(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ForecastResponse(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    days_ahead: int
    predicted_demand: float
    current_stock: float
    stock_after_demand: float
    needs_reorder: bool
    reorder_point: float
    confidence: Confidence
    r2_score: float | None
    generated_at: datetime


class AlertResponse(BaseModel):
    product_id: int
    product_sku: str
    product_name: str
    current_stock: float
    reorder_point: float
    predicted_demand: float
    days_ahead: int
    stock_after_demand: float
    confidence: Confidence
