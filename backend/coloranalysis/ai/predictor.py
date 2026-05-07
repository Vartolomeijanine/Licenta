from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from coloranalysis.ai.color_features import ColorFeatureService


class SeasonPredictorService:
    """Runtime predictor backed by the trained model saved in dataset/best_season_model.pkl."""

    EPS = 1e-6

    def __init__(self) -> None:
        self.feature_service = ColorFeatureService()
        self.model_path = Path(__file__).resolve().parents[2] / "dataset" / "best_season_model.pkl"
        self.model = None
        self.feature_names: list[str] = []
        self._load_model()

    def _load_model(self) -> None:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Trained model not found: {self.model_path}")

        self.model = joblib.load(self.model_path)
        self.feature_names = list(getattr(self.model, "feature_names_in_", []))

    def _safe_diff(self, a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return round(abs(a - b), 2)

    def _safe_ratio(self, a: float | None, b: float | None) -> float | None:
        if a is None or b is None or b == 0:
            return None
        return round(a / b, 4)

    def _safe_normalized_contrast(self, a: float | None, b: float | None) -> float | None:
        if a is None or b is None:
            return None
        return round(abs(a - b) / max(a, b, self.EPS), 4)

    def _safe_average(self, values: list[float | None], decimals: int = 4) -> float | None:
        valid = [v for v in values if v is not None]
        if not valid:
            return None
        return round(sum(valid) / len(valid), decimals)

    def _hue_distance(self, h1: float | None, h2: float | None) -> float | None:
        if h1 is None or h2 is None:
            return None
        diff = abs(h1 - h2)
        return round(min(diff, 360 - diff), 2)

    def _get_hair_color(self, hair_summary: dict[str, Any]) -> dict[str, float | None]:
        if not hair_summary.get("used_observed_hair"):
            return {"L": None, "a": None, "b": None, "C": None, "H": None}

        hair_lab = hair_summary.get("hair_lab_lch") or {}
        return {
            "L": hair_lab.get("L"),
            "a": hair_lab.get("a"),
            "b": hair_lab.get("b"),
            "C": hair_lab.get("C"),
            "H": hair_lab.get("H"),
        }

    def _build_model_row(
        self,
        features: dict[str, Any],
        is_hair_visible: str,
        is_hair_natural: str,
        natural_hair_color: str | None,
    ) -> pd.DataFrame:
        skin = features["skin"]
        eyes = features.get("eyes") or {}
        hair = features.get("hair") or {}

        skin_agg = skin["aggregated_features"]
        eye_agg = eyes.get("aggregated_features") or {}
        hair_color = self._get_hair_color(hair)

        skin_L = skin_agg.get("avg_skin_L")
        skin_a = skin_agg.get("avg_skin_a")
        skin_b = skin_agg.get("avg_skin_b_lab")
        skin_C = skin_agg.get("avg_skin_C")
        skin_H = skin_agg.get("avg_skin_H")
        skin_darkness = round(100 - skin_L, 2) if skin_L is not None else None

        eye_L = eye_agg.get("avg_eye_L")
        eye_a = eye_agg.get("avg_eye_a")
        eye_b = eye_agg.get("avg_eye_b_lab")
        eye_C = eye_agg.get("avg_eye_C")
        eye_H = eye_agg.get("avg_eye_H")
        eye_darkness = eyes.get("aggregated_features", {}).get("eye_darkness") if eyes.get("aggregated_features") else None

        hair_L = hair_color["L"]
        hair_a = hair_color["a"]
        hair_b = hair_color["b"]
        hair_C = hair_color["C"]
        hair_H = hair_color["H"]
        hair_darkness = round(100 - hair_L, 2) if hair_L is not None else None

        skin_eye_L_diff = self._safe_diff(skin_L, eye_L)
        skin_hair_L_diff = self._safe_diff(skin_L, hair_L)
        eye_hair_L_diff = self._safe_diff(eye_L, hair_L)

        normalized_skin_eye_L_contrast = self._safe_normalized_contrast(skin_L, eye_L)
        normalized_skin_hair_L_contrast = self._safe_normalized_contrast(skin_L, hair_L)
        normalized_eye_hair_L_contrast = self._safe_normalized_contrast(eye_L, hair_L)
        overall_contrast_score = self._safe_average(
            [normalized_skin_eye_L_contrast, normalized_skin_hair_L_contrast, normalized_eye_hair_L_contrast],
            decimals=4,
        )

        skin_eye_C_diff = self._safe_diff(skin_C, eye_C)
        skin_hair_C_diff = self._safe_diff(skin_C, hair_C)
        eye_hair_C_diff = self._safe_diff(eye_C, hair_C)

        skin_eye_C_ratio = self._safe_ratio(skin_C, eye_C)
        skin_hair_C_ratio = self._safe_ratio(skin_C, hair_C)
        eye_hair_C_ratio = self._safe_ratio(eye_C, hair_C)
        overall_chroma_score = self._safe_average([skin_C, eye_C, hair_C], decimals=2)

        skin_eye_H_diff = self._hue_distance(skin_H, eye_H)
        skin_hair_H_diff = self._hue_distance(skin_H, hair_H)
        eye_hair_H_diff = self._hue_distance(eye_H, hair_H)

        skin_eye_a_diff = self._safe_diff(skin_a, eye_a)
        skin_eye_b_diff = self._safe_diff(skin_b, eye_b)
        skin_hair_a_diff = self._safe_diff(skin_a, hair_a)
        skin_hair_b_diff = self._safe_diff(skin_b, hair_b)

        lightness_values = [v for v in [skin_L, eye_L, hair_L] if v is not None]
        true_lightness_range = None
        if lightness_values:
            true_lightness_range = round(max(lightness_values) - min(lightness_values), 2)

        normalized_true_contrast = None
        if true_lightness_range is not None and skin_L is not None:
            normalized_true_contrast = round(true_lightness_range / (skin_L + self.EPS), 4)

        global_contrast = self._safe_average([skin_eye_L_diff, skin_hair_L_diff, eye_hair_L_diff], decimals=4)
        hair_skin_lightness_ratio = self._safe_ratio(hair_L, skin_L)
        eye_skin_lightness_ratio = self._safe_ratio(eye_L, skin_L)
        hair_skin_darkness_diff = self._safe_diff(hair_darkness, skin_darkness)
        chroma_balance = self._safe_average([skin_C, eye_C, hair_C], decimals=4)
        eye_skin_chroma_ratio = self._safe_ratio(eye_C, skin_C)
        hair_skin_chroma_ratio = self._safe_ratio(hair_C, skin_C)
        skin_undertone_index = None
        if skin_b is not None and skin_a is not None:
            skin_undertone_index = round(skin_b / (abs(skin_a) + self.EPS), 4)

        warm_cool_score = self._safe_average([skin_b, eye_b, hair_b], decimals=4)
        a_axis_balance = self._safe_average([skin_a, eye_a, hair_a], decimals=4)
        warm_vs_cool_skin = None if skin_b is None or skin_a is None else round(skin_b - skin_a, 2)
        skin_eye_warmth_diff = self._safe_diff(skin_b, eye_b)
        skin_hair_warmth_diff = self._safe_diff(skin_b, hair_b)
        hair_skin_warmth_diff = self._safe_diff(hair_b, skin_b)

        row = {
            "avg_skin_r": skin_agg.get("avg_skin_r"),
            "avg_skin_g": skin_agg.get("avg_skin_g"),
            "avg_skin_b": skin_agg.get("avg_skin_b"),
            "avg_skin_L": skin_L,
            "avg_skin_a": skin_a,
            "avg_skin_b_lab": skin_b,
            "avg_skin_C": skin_C,
            "skin_darkness": skin_darkness,
            "cheek_L_diff": skin_agg.get("cheek_L_diff"),
            "cheek_a_diff": skin_agg.get("cheek_a_diff"),
            "cheek_b_diff": skin_agg.get("cheek_b_diff"),
            "cheek_C_diff": skin_agg.get("cheek_C_diff"),
            "forehead_vs_cheeks_L_diff": skin_agg.get("forehead_vs_cheeks_L_diff"),
            "forehead_vs_cheeks_a_diff": skin_agg.get("forehead_vs_cheeks_a_diff"),
            "forehead_vs_cheeks_b_diff": skin_agg.get("forehead_vs_cheeks_b_diff"),
            "forehead_vs_cheeks_C_diff": skin_agg.get("forehead_vs_cheeks_C_diff"),
            "avg_eye_L": eye_L,
            "avg_eye_a": eye_a,
            "avg_eye_b_lab": eye_b,
            "avg_eye_C": eye_C,
            "eye_vs_skin_L_diff": eye_agg.get("eye_vs_skin_L_diff") if eye_agg else None,
            "eye_darkness": eye_darkness,
            "is_hair_visible": is_hair_visible,
            "is_hair_natural": is_hair_natural,
            "natural_hair_color": natural_hair_color,
            "used_observed_hair": str(hair.get("used_observed_hair", False)),
            "hair_L": hair_L,
            "hair_a": hair_a,
            "hair_b_lab": hair_b,
            "hair_C": hair_C,
            "hair_darkness": hair_darkness,
            "skin_eye_L_diff": skin_eye_L_diff,
            "skin_hair_L_diff": skin_hair_L_diff,
            "eye_hair_L_diff": eye_hair_L_diff,
            "normalized_skin_eye_L_contrast": normalized_skin_eye_L_contrast,
            "normalized_skin_hair_L_contrast": normalized_skin_hair_L_contrast,
            "normalized_eye_hair_L_contrast": normalized_eye_hair_L_contrast,
            "overall_contrast_score": overall_contrast_score,
            "skin_eye_C_diff": skin_eye_C_diff,
            "skin_hair_C_diff": skin_hair_C_diff,
            "eye_hair_C_diff": eye_hair_C_diff,
            "skin_eye_C_ratio": skin_eye_C_ratio,
            "skin_hair_C_ratio": skin_hair_C_ratio,
            "eye_hair_C_ratio": eye_hair_C_ratio,
            "overall_chroma_score": overall_chroma_score,
            "skin_eye_H_diff": skin_eye_H_diff,
            "skin_hair_H_diff": skin_hair_H_diff,
            "eye_hair_H_diff": eye_hair_H_diff,
            "skin_eye_a_diff": skin_eye_a_diff,
            "skin_eye_b_diff": skin_eye_b_diff,
            "skin_hair_a_diff": skin_hair_a_diff,
            "skin_hair_b_diff": skin_hair_b_diff,
            "true_lightness_range": true_lightness_range,
            "normalized_true_contrast": normalized_true_contrast,
            "global_contrast": global_contrast,
            "hair_skin_lightness_ratio": hair_skin_lightness_ratio,
            "eye_skin_lightness_ratio": eye_skin_lightness_ratio,
            "hair_skin_darkness_diff": hair_skin_darkness_diff,
            "chroma_balance": chroma_balance,
            "eye_skin_chroma_ratio": eye_skin_chroma_ratio,
            "hair_skin_chroma_ratio": hair_skin_chroma_ratio,
            "skin_undertone_index": skin_undertone_index,
            "warm_cool_score": warm_cool_score,
            "a_axis_balance": a_axis_balance,
            "warm_vs_cool_skin": warm_vs_cool_skin,
            "skin_eye_warmth_diff": skin_eye_warmth_diff,
            "skin_hair_warmth_diff": skin_hair_warmth_diff,
            "hair_skin_warmth_diff": hair_skin_warmth_diff,
        }

        if self.feature_names:
            for name in self.feature_names:
                row.setdefault(name, None)

        return pd.DataFrame([row], columns=self.feature_names or None)

    def _predict_with_model(self, row: pd.DataFrame) -> dict[str, Any]:
        prediction = self.model.predict(row)[0]

        confidence = None
        if hasattr(self.model, "predict_proba"):
            probabilities = self.model.predict_proba(row)[0]
            class_index = int(list(self.model.classes_).index(prediction))
            confidence = round(float(probabilities[class_index]), 4)

        return {
            "predicted_season": str(prediction).lower(),
            "predicted_season_label": str(prediction).title(),
            "confidence": confidence,
        }

    def predict_from_image(
        self,
        image_path: str,
        is_hair_visible: str = "yes",
        is_hair_natural: str = "yes",
        natural_hair_color: str | None = None,
    ) -> dict[str, Any]:
        result = self.feature_service.extract_color_features(
            image_path,
            is_hair_visible=is_hair_visible,
            is_hair_natural=is_hair_natural,
            natural_hair_color=natural_hair_color,
        )

        if not result.get("success"):
            return result

        row = self._build_model_row(
            result["features"],
            is_hair_visible=is_hair_visible,
            is_hair_natural=is_hair_natural,
            natural_hair_color=natural_hair_color,
        )
        prediction = self._predict_with_model(row)

        return {
            "success": True,
            "features": result["features"],
            "prediction": prediction,
        }