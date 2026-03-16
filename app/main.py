from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.database import engine, Base
import app.models  # noqa: F401 — ensures models are registered before create_all
from app.routers import products, sales, forecast


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Stock Forecast API",
    description=(
        "REST API for inventory demand forecasting. "
        "Uses historical sales data and Linear Regression to predict future demand "
        "and alert when stock is likely to fall below the reorder point."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(products.router)
app.include_router(sales.router)
app.include_router(forecast.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
