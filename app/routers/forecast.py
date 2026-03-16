from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.schemas.forecast import ForecastResponse, AlertResponse
from app.services import forecast as forecast_service

router = APIRouter(prefix="/forecast", tags=["Forecast"])


@router.get("/products/{product_id}", response_model=ForecastResponse)
def forecast_product(
    product_id: int,
    days_ahead: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return forecast_service.get_forecast(db, product, days_ahead)


@router.get("/alerts", response_model=list[AlertResponse])
def reorder_alerts(
    days_ahead: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """
    Returns all products that are predicted to fall below their reorder point
    within the given period.
    """
    return forecast_service.get_reorder_alerts(db, days_ahead)
