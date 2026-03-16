from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.product import Product
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleResponse, SaleBulkCreate

router = APIRouter(prefix="/products/{product_id}/sales", tags=["Sales"])


def _get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=SaleResponse, status_code=status.HTTP_201_CREATED)
def create_sale(product_id: int, payload: SaleCreate, db: Session = Depends(get_db)):
    _get_product_or_404(product_id, db)
    sale = Sale(product_id=product_id, **payload.model_dump())
    db.add(sale)
    db.commit()
    db.refresh(sale)
    return sale


@router.post("/bulk", response_model=list[SaleResponse], status_code=status.HTTP_201_CREATED)
def create_sales_bulk(product_id: int, payload: SaleBulkCreate, db: Session = Depends(get_db)):
    _get_product_or_404(product_id, db)
    sales = [Sale(product_id=product_id, **s.model_dump()) for s in payload.sales]
    db.add_all(sales)
    db.commit()
    for s in sales:
        db.refresh(s)
    return sales


@router.get("/", response_model=list[SaleResponse])
def list_sales(product_id: int, db: Session = Depends(get_db)):
    _get_product_or_404(product_id, db)
    return db.query(Sale).filter(Sale.product_id == product_id).order_by(Sale.date).all()
