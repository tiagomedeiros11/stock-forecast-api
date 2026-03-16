from datetime import date, timedelta
from app.ml.model import predict


def _make_history(n_days: int, base_qty: float = 10.0) -> list[dict]:
    base = date(2024, 1, 1)
    return [{"date": str(base + timedelta(days=i)), "quantity": base_qty} for i in range(n_days)]


def test_predict_empty_history():
    result = predict([])
    assert result.predicted_quantity == 0.0
    assert result.confidence == "low"
    assert result.r2_score is None


def test_predict_few_samples_uses_moving_average():
    history = _make_history(3, base_qty=10.0)
    result = predict(history, days_ahead=10)
    assert result.predicted_quantity == 100.0  # 10 * 10 days
    assert result.confidence == "low"
    assert result.r2_score is None


def test_predict_enough_samples_uses_regression():
    history = _make_history(30, base_qty=10.0)
    result = predict(history, days_ahead=30)
    assert result.predicted_quantity > 0
    assert result.r2_score is not None


def test_predict_never_returns_negative():
    # Decreasing trend that would predict negative values
    base = date(2024, 1, 1)
    history = [{"date": str(base + timedelta(days=i)), "quantity": max(0, 50 - i * 5)} for i in range(20)]
    result = predict(history, days_ahead=30)
    assert result.predicted_quantity >= 0.0


def test_confidence_levels():
    # Perfect linear trend → high confidence
    base = date(2024, 1, 1)
    history = [{"date": str(base + timedelta(days=i)), "quantity": float(i + 1)} for i in range(30)]
    result = predict(history, days_ahead=30)
    assert result.confidence in ("medium", "high")
