import logging
import math

logger = logging.getLogger(__name__)


class RecommendationService:
    """Business logic for generating recommendations."""

    def generate_recommendation(self, current_prices, prediction):
        try:
            if not isinstance(current_prices, list) or not current_prices or not isinstance(prediction, dict):
                return self.default_recommendation()

            normalized_prices = []
            for item in current_prices:
                if not isinstance(item, dict):
                    continue
                price = item.get("price", item.get("modal_price"))
                if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
                    continue
                normalized_prices.append({
                    "price": float(price),
                    "mandi": item.get("mandi") or item.get("mandi_name") or item.get("market") or item.get("district") or "Unknown market"
                })

            if not normalized_prices:
                return self.default_recommendation()

            predicted_prices = prediction.get("predicted_prices")
            if predicted_prices is None:
                predicted_prices = prediction.get("predictedPrices", [])

            normalized_predictions = []
            for item in predicted_prices if isinstance(predicted_prices, list) else []:
                if isinstance(item, dict):
                    price = item.get("price")
                    date = item.get("date")
                else:
                    price = item
                    date = None
                if isinstance(price, bool) or not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
                    continue
                normalized_predictions.append({"price": float(price), "date": date})

            if not normalized_predictions:
                return self.default_recommendation()

            avg_current = sum(item["price"] for item in normalized_prices) / len(normalized_prices)
            best_prediction_index = max(
                range(len(normalized_predictions)),
                key=lambda index: normalized_predictions[index]["price"]
            )
            max_predicted = normalized_predictions[best_prediction_index]["price"]
            potential_gain = max_predicted - avg_current
            gain_percent = (potential_gain / avg_current) * 100 if avg_current > 0 else 0
            best_market = max(normalized_prices, key=lambda item: item["price"])

            optimal_day = prediction.get("optimalDay")
            if isinstance(optimal_day, bool) or not isinstance(optimal_day, int) or not 1 <= optimal_day <= len(normalized_predictions):
                optimal_day = best_prediction_index + 1

            confidence_value = prediction.get("confidence", 0)
            if isinstance(confidence_value, str):
                confidence_is_high = confidence_value.casefold() in {"high", "0.8", "0.9", "1.0"}
            elif isinstance(confidence_value, (int, float)) and not isinstance(confidence_value, bool):
                confidence_is_high = confidence_value > 0.75
            else:
                confidence_is_high = False

            if gain_percent > 5:
                action = "WAIT"
                message = f"Wait {optimal_day} days. Price expected to rise by ₹{potential_gain:.0f} ({gain_percent:.1f}%)"
                confidence = "HIGH" if confidence_is_high else "MEDIUM"
            elif gain_percent > 2:
                action = "WAIT"
                message = f"Consider waiting {optimal_day} days for ₹{potential_gain:.0f} gain"
                confidence = "MEDIUM"
            else:
                action = "SELL NOW"
                message = f"Current prices are good. Sell at {best_market['mandi']}"
                confidence = "HIGH"

            return {
                "action": action,
                "message": message,
                "confidence": confidence,
                "expectedGain": round(potential_gain, 2),
                "gainPercent": round(gain_percent, 2),
                "bestMarket": best_market["mandi"],
                "bestPrice": round(best_market["price"], 2),
                "optimalDay": optimal_day,
                "recommendedDate": normalized_predictions[optimal_day - 1]["date"]
            }

        except Exception as e:
            logger.error("Error generating recommendation: %s", e, exc_info=True)
            return self.default_recommendation()

    def default_recommendation(self):
        return {
            "action": "INSUFFICIENT DATA",
            "message": "Not enough data to make a recommendation",
            "confidence": "LOW",
            "expectedGain": 0,
            "gainPercent": 0
        }

    def calculate_total_gain(self, recommendation, quantity):
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, (int, float))
            or not math.isfinite(quantity)
            or quantity <= 0
            or recommendation.get("action") == "INSUFFICIENT DATA"
        ):
            return None

        expected_gain_per_quintal = recommendation.get("expectedGain", 0)
        if isinstance(expected_gain_per_quintal, bool) or not isinstance(expected_gain_per_quintal, (int, float)):
            return None

        total_gain = expected_gain_per_quintal * quantity
        return {
            "perQuintal": expected_gain_per_quintal,
            "total": round(total_gain, 2),
            "quantity": quantity
        }
