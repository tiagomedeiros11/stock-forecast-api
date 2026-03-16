import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass


@dataclass
class ForecastResult:
    predicted_quantity: float
    confidence: str
    r2_score: float | None


MIN_SAMPLES_FOR_REGRESSION = 7


def predict(sales_history: list[dict], days_ahead: int = 30) -> ForecastResult:
    """
    Predicts total demand for the next `days_ahead` days based on historical sales.

    Uses Linear Regression when enough data is available (>= 7 data points),
    otherwise falls back to a simple moving average.

    Args:
        sales_history: list of dicts with keys 'date' (str or date) and 'quantity' (float)
        days_ahead: number of days to forecast

    Returns:
        ForecastResult with predicted_quantity, confidence level and r2_score
    """
    if not sales_history:
        return ForecastResult(predicted_quantity=0.0, confidence="low", r2_score=None)

    df = _prepare_dataframe(sales_history)

    if len(df) < MIN_SAMPLES_FOR_REGRESSION:
        return _moving_average_forecast(df, days_ahead)

    return _linear_regression_forecast(df, days_ahead)


def _prepare_dataframe(sales_history: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(sales_history)
    df["date"] = pd.to_datetime(df["date"])
    df = df.groupby("date")["quantity"].sum().reset_index()
    df = df.sort_values("date").reset_index(drop=True)
    df["day_num"] = (df["date"] - df["date"].min()).dt.days
    return df


def _moving_average_forecast(df: pd.DataFrame, days_ahead: int) -> ForecastResult:
    avg_daily = df["quantity"].mean()
    predicted = round(avg_daily * days_ahead, 2)
    return ForecastResult(predicted_quantity=predicted, confidence="low", r2_score=None)


def _linear_regression_forecast(df: pd.DataFrame, days_ahead: int) -> ForecastResult:
    X = df["day_num"].values.reshape(-1, 1)
    y = df["quantity"].values

    model = LinearRegression()
    model.fit(X, y)

    last_day = int(df["day_num"].max())
    future_days = np.arange(last_day + 1, last_day + days_ahead + 1).reshape(-1, 1)
    predictions = model.predict(future_days)

    predicted = round(float(max(0.0, predictions.sum())), 2)
    r2 = round(float(model.score(X, y)), 3)
    confidence = _confidence_from_r2(r2)

    return ForecastResult(predicted_quantity=predicted, confidence=confidence, r2_score=r2)


def _confidence_from_r2(r2: float) -> str:
    if r2 >= 0.7:
        return "high"
    if r2 >= 0.4:
        return "medium"
    return "low"
