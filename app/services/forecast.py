from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.sale import Sale
from app.ml import model as ml
from app.schemas.forecast import ForecastResponse, AlertResponse, Confidence


def get_forecast(db: Session, product: Product, days_ahead: int) -> ForecastResponse:
    sales_history = _load_sales_history(db, product.id)
    result = ml.predict(sales_history, days_ahead)

    stock_after = round(product.current_stock - result.predicted_quantity, 2)

    return ForecastResponse(
        product_id=product.id,
        product_sku=product.sku,
        product_name=product.name,
        days_ahead=days_ahead,
        predicted_demand=result.predicted_quantity,
        current_stock=product.current_stock,
        stock_after_demand=stock_after,
        needs_reorder=stock_after < product.reorder_point,
        reorder_point=product.reorder_point,
        confidence=Confidence(result.confidence),
        r2_score=result.r2_score,
        generated_at=datetime.now(timezone.utc),
    )


def get_reorder_alerts(db: Session, days_ahead: int) -> list[AlertResponse]:
    products = db.query(Product).all()
    alerts = []

    for product in products:
        sales_history = _load_sales_history(db, product.id)
        result = ml.predict(sales_history, days_ahead)
        stock_after = round(product.current_stock - result.predicted_quantity, 2)

        if stock_after < product.reorder_point:
            alerts.append(
                AlertResponse(
                    product_id=product.id,
                    product_sku=product.sku,
                    product_name=product.name,
                    current_stock=product.current_stock,
                    reorder_point=product.reorder_point,
                    predicted_demand=result.predicted_quantity,
                    days_ahead=days_ahead,
                    stock_after_demand=stock_after,
                    confidence=Confidence(result.confidence),
                )
            )

    return alerts


def _load_sales_history(db: Session, product_id: int) -> list[dict]:
    sales = db.query(Sale).filter(Sale.product_id == product_id).all()
    return [{"date": s.date, "quantity": s.quantity} for s in sales]
