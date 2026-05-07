from __future__ import annotations

from typing import Any

from coloranalysis.ai.color_features import ColorFeatureService


class SeasonPredictorService:
    def __init__(self) -> None:
        self.feature_service = ColorFeatureService()

    def _predict_from_features(self, features: dict[str, float]) -> dict[str, Any]:
        avg_l = features["avg_skin_L"]
        avg_c = features["avg_skin_C"]
        avg_h = features["avg_skin_H"]

        # euristică simplă, temporară
        if avg_h >= 50 and avg_l >= 75 and avg_c >= 20:
            season = "Spring"
            reason = "warm hue, high lightness, clear chroma"
        elif avg_h >= 50 and avg_l < 75:
            season = "Autumn"
            reason = "warm hue, lower lightness"
        elif avg_h < 50 and avg_l >= 70:
            season = "Summer"
            reason = "cooler hue with relatively light skin profile"
        else:
            season = "Winter"
            reason = "cooler profile with stronger/deeper appearance"

        return {
            "predicted_season": season,
            "reason": reason,
            "used_features": {
                "avg_skin_L": avg_l,
                "avg_skin_C": avg_c,
                "avg_skin_H": avg_h,
            }
        }

    def predict_from_image(self, image_path: str) -> dict[str, Any]:
        result = self.feature_service.extract_color_features(image_path)

        if not result.get("success"):
            return result

        aggregated_features = result["features"]["aggregated_features"]
        prediction = self._predict_from_features(aggregated_features)

        return {
            "success": True,
            "features": result["features"],
            "prediction": prediction,
        }