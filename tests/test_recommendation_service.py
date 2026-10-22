import pytest

from services.recommendation_service import RecommendationService


@pytest.fixture
def service():
    return RecommendationService()


def test_recommendation_accepts_prediction_api_numeric_price_list(service):
    result = service.generate_recommendation(
        [{"modal_price": 2000, "mandi_name": "Indore APMC"}],
        {
            "predicted_prices": [2010, 2040, 2080],
            "confidence": "high"
        }
    )

    assert result["action"] == "WAIT"
    assert result["bestMarket"] == "Indore APMC"
    assert result["bestPrice"] == 2000
    assert result["expectedGain"] == 80
    assert result["optimalDay"] == 3
    assert result["recommendedDate"] is None


def test_recommendation_accepts_legacy_object_predictions(service):
    result = service.generate_recommendation(
        [{"price": 100, "mandi": "Market A"}],
        {
            "predictedPrices": [
                {"price": 101, "date": "2026-10-24"},
                {"price": 110, "date": "2026-10-25"}
            ],
            "confidence": 0.9,
            "optimalDay": 2
        }
    )

    assert result["action"] == "WAIT"
    assert result["recommendedDate"] == "2026-10-25"
    assert result["confidence"] == "HIGH"


def test_recommendation_returns_insufficient_data_for_invalid_prices(service):
    result = service.generate_recommendation(
        [{"modal_price": "unknown", "mandi_name": "Indore"}],
        {"predicted_prices": [2100]}
    )

    assert result["action"] == "INSUFFICIENT DATA"


def test_calculate_total_gain_validates_quantity(service):
    recommendation = {"action": "WAIT", "expectedGain": 25}

    assert service.calculate_total_gain(recommendation, 10)["total"] == 250
    assert service.calculate_total_gain(recommendation, -1) is None
    assert service.calculate_total_gain(recommendation, True) is None
