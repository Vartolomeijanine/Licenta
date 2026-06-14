from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import cv2
import numpy as np
from skimage.color import rgb2lab

from coloranalysis.ai.region_extraction import RegionExtractionService


class ColorFeatureService:
    def __init__(self, patch_size: int = 9, stride: int = 6) -> None:
        self.region_service = RegionExtractionService()
        self.patch_size = patch_size
        self.stride = stride

    def _extract_region_pixels(self, image: np.ndarray, region: dict[str, int]) -> np.ndarray:
        x1, y1, x2, y2 = region["x1"], region["y1"], region["x2"], region["y2"]
        return image[y1:y2, x1:x2]

    def _rgb_to_lab_lch(self, rgb: list[int] | np.ndarray) -> dict[str, float]:
        rgb_array = np.array([[rgb]], dtype=np.float32) / 255.0
        lab = rgb2lab(rgb_array)[0][0]

        l = float(lab[0])
        a = float(lab[1])
        b = float(lab[2])

        c = float(np.sqrt(a ** 2 + b ** 2))
        h = float(np.degrees(np.arctan2(b, a)))
        if h < 0:
            h += 360

        return {
            "L": round(l, 2),
            "a": round(a, 2),
            "b": round(b, 2),
            "C": round(c, 2),
            "H": round(h, 2),
        }

    def _extract_patches(self, region_pixels: np.ndarray) -> list[np.ndarray]:
        patches: list[np.ndarray] = []

        if region_pixels.size == 0:
            return patches

        h, w = region_pixels.shape[:2]
        ps = self.patch_size
        st = self.stride

        if h < ps or w < ps:
            return patches

        for y in range(0, h - ps + 1, st):
            for x in range(0, w - ps + 1, st):
                patches.append(region_pixels[y:y + ps, x:x + ps])

        return patches

    def _is_valid_skin_patch(self, patch_bgr: np.ndarray) -> bool:
        if patch_bgr.size == 0:
            return False

        patch_rgb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2RGB)
        patch_rgb_float = patch_rgb.astype(np.float32) / 255.0

        brightness = float(patch_rgb_float.mean())
        std_val = float(patch_rgb_float.std())

        if brightness < 0.15:
            return False

        if brightness > 0.95:
            return False

        if std_val > 0.22:
            return False

        return True

    def _is_valid_generic_patch(self, patch_bgr: np.ndarray) -> bool:
        if patch_bgr.size == 0:
            return False

        patch_rgb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2RGB)
        patch_rgb_float = patch_rgb.astype(np.float32) / 255.0

        brightness = float(patch_rgb_float.mean())
        if brightness < 0.05 or brightness > 0.98:
            return False

        return True

    def _is_valid_eye_patch(self, patch_bgr: np.ndarray) -> bool:
        if patch_bgr.size == 0:
            return False

        patch_rgb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2RGB)
        patch_rgb_float = patch_rgb.astype(np.float32) / 255.0

        brightness = float(patch_rgb_float.mean())
        std_val = float(patch_rgb_float.std())

        if brightness < 0.03 or brightness > 0.95:
            return False

        if std_val < 0.03:
            return False

        return True

    def _patch_mean_rgb(self, patch_bgr: np.ndarray) -> list[int]:
        patch_rgb = cv2.cvtColor(patch_bgr, cv2.COLOR_BGR2RGB)
        mean_values = patch_rgb.mean(axis=(0, 1))
        return [int(v) for v in mean_values]

    def _extract_valid_patch_features(
        self,
        region_pixels: np.ndarray,
        patch_validator: Callable[[np.ndarray], bool],
    ) -> tuple[list[list[int]], list[dict[str, float]]]:
        valid_patch_rgbs: list[list[int]] = []
        valid_patch_lab_lch: list[dict[str, float]] = []

        patches = self._extract_patches(region_pixels)

        for patch in patches:
            if not patch_validator(patch):
                continue

            patch_rgb = self._patch_mean_rgb(patch)
            patch_lab_lch = self._rgb_to_lab_lch(patch_rgb)

            valid_patch_rgbs.append(patch_rgb)
            valid_patch_lab_lch.append(patch_lab_lch)

        return valid_patch_rgbs, valid_patch_lab_lch

    def _circular_mean_degrees(self, angles_deg: list[float]) -> float:
        if not angles_deg:
            return 0.0

        angles_rad = np.radians(angles_deg)
        mean_sin = np.mean(np.sin(angles_rad))
        mean_cos = np.mean(np.cos(angles_rad))

        mean_angle_rad = np.arctan2(mean_sin, mean_cos)
        mean_angle_deg = float(np.degrees(mean_angle_rad))

        if mean_angle_deg < 0:
            mean_angle_deg += 360

        return round(mean_angle_deg, 2)

    def _mean_rgb_from_patch_list(self, patch_rgbs: list[list[int]]) -> list[int]:
        if not patch_rgbs:
            return [0, 0, 0]

        arr = np.array(patch_rgbs, dtype=np.float32)
        mean_values = arr.mean(axis=0)
        return [int(round(v)) for v in mean_values]

    def _aggregate_patch_lab_lch(self, patch_lab_lch: list[dict[str, float]]) -> dict[str, float]:
        if not patch_lab_lch:
            return {
                "L": 0.0,
                "a": 0.0,
                "b": 0.0,
                "C": 0.0,
                "H": 0.0,
            }

        l_values = [item["L"] for item in patch_lab_lch]
        a_values = [item["a"] for item in patch_lab_lch]
        b_values = [item["b"] for item in patch_lab_lch]
        c_values = [item["C"] for item in patch_lab_lch]
        h_values = [item["H"] for item in patch_lab_lch]

        return {
            "L": round(float(np.mean(l_values)), 2),
            "a": round(float(np.mean(a_values)), 2),
            "b": round(float(np.mean(b_values)), 2),
            "C": round(float(np.mean(c_values)), 2),
            "H": self._circular_mean_degrees(h_values),
        }

    def _build_skin_features(
        self,
        left_rgb: list[int],
        right_rgb: list[int],
        forehead_rgb: list[int],
        left_lab_lch: dict[str, float],
        right_lab_lch: dict[str, float],
        forehead_lab_lch: dict[str, float],
    ) -> dict[str, float]:
        avg_skin_r = round((left_rgb[0] + right_rgb[0] + forehead_rgb[0]) / 3, 2)
        avg_skin_g = round((left_rgb[1] + right_rgb[1] + forehead_rgb[1]) / 3, 2)
        avg_skin_b = round((left_rgb[2] + right_rgb[2] + forehead_rgb[2]) / 3, 2)

        avg_skin_l = round((left_lab_lch["L"] + right_lab_lch["L"] + forehead_lab_lch["L"]) / 3, 2)
        avg_skin_a = round((left_lab_lch["a"] + right_lab_lch["a"] + forehead_lab_lch["a"]) / 3, 2)
        avg_skin_b_lab = round((left_lab_lch["b"] + right_lab_lch["b"] + forehead_lab_lch["b"]) / 3, 2)
        avg_skin_c = round((left_lab_lch["C"] + right_lab_lch["C"] + forehead_lab_lch["C"]) / 3, 2)
        avg_skin_h = self._circular_mean_degrees([
            left_lab_lch["H"],
            right_lab_lch["H"],
            forehead_lab_lch["H"],
        ])

        cheek_l_diff = round(abs(left_lab_lch["L"] - right_lab_lch["L"]), 2)
        cheek_a_diff = round(abs(left_lab_lch["a"] - right_lab_lch["a"]), 2)
        cheek_b_diff = round(abs(left_lab_lch["b"] - right_lab_lch["b"]), 2)
        cheek_c_diff = round(abs(left_lab_lch["C"] - right_lab_lch["C"]), 2)

        cheek_h_diff_raw = abs(left_lab_lch["H"] - right_lab_lch["H"])
        cheek_h_diff = round(min(cheek_h_diff_raw, 360 - cheek_h_diff_raw), 2)

        cheeks_avg_l = (left_lab_lch["L"] + right_lab_lch["L"]) / 2
        cheeks_avg_a = (left_lab_lch["a"] + right_lab_lch["a"]) / 2
        cheeks_avg_b = (left_lab_lch["b"] + right_lab_lch["b"]) / 2
        cheeks_avg_c = (left_lab_lch["C"] + right_lab_lch["C"]) / 2
        cheeks_avg_h = self._circular_mean_degrees([left_lab_lch["H"], right_lab_lch["H"]])

        forehead_vs_cheeks_l_diff = round(abs(forehead_lab_lch["L"] - cheeks_avg_l), 2)
        forehead_vs_cheeks_a_diff = round(abs(forehead_lab_lch["a"] - cheeks_avg_a), 2)
        forehead_vs_cheeks_b_diff = round(abs(forehead_lab_lch["b"] - cheeks_avg_b), 2)
        forehead_vs_cheeks_c_diff = round(abs(forehead_lab_lch["C"] - cheeks_avg_c), 2)

        forehead_h_diff_raw = abs(forehead_lab_lch["H"] - cheeks_avg_h)
        forehead_vs_cheeks_h_diff = round(min(forehead_h_diff_raw, 360 - forehead_h_diff_raw), 2)

        return {
            "avg_skin_r": avg_skin_r,
            "avg_skin_g": avg_skin_g,
            "avg_skin_b": avg_skin_b,

            "avg_skin_L": avg_skin_l,
            "avg_skin_a": avg_skin_a,
            "avg_skin_b_lab": avg_skin_b_lab,
            "avg_skin_C": avg_skin_c,
            "avg_skin_H": avg_skin_h,

            "cheek_L_diff": cheek_l_diff,
            "cheek_a_diff": cheek_a_diff,
            "cheek_b_diff": cheek_b_diff,
            "cheek_C_diff": cheek_c_diff,
            "cheek_H_diff": cheek_h_diff,

            "forehead_vs_cheeks_L_diff": forehead_vs_cheeks_l_diff,
            "forehead_vs_cheeks_a_diff": forehead_vs_cheeks_a_diff,
            "forehead_vs_cheeks_b_diff": forehead_vs_cheeks_b_diff,
            "forehead_vs_cheeks_C_diff": forehead_vs_cheeks_c_diff,
            "forehead_vs_cheeks_H_diff": forehead_vs_cheeks_h_diff,
        }

    def _build_eye_features(
        self,
        left_eye_rgb: list[int],
        right_eye_rgb: list[int],
        left_eye_lab_lch: dict[str, float],
        right_eye_lab_lch: dict[str, float],
        skin_features: dict[str, float],
    ) -> dict[str, float]:
        avg_eye_r = round((left_eye_rgb[0] + right_eye_rgb[0]) / 2, 2)
        avg_eye_g = round((left_eye_rgb[1] + right_eye_rgb[1]) / 2, 2)
        avg_eye_b = round((left_eye_rgb[2] + right_eye_rgb[2]) / 2, 2)

        avg_eye_l = round((left_eye_lab_lch["L"] + right_eye_lab_lch["L"]) / 2, 2)
        avg_eye_a = round((left_eye_lab_lch["a"] + right_eye_lab_lch["a"]) / 2, 2)
        avg_eye_b_lab = round((left_eye_lab_lch["b"] + right_eye_lab_lch["b"]) / 2, 2)
        avg_eye_c = round((left_eye_lab_lch["C"] + right_eye_lab_lch["C"]) / 2, 2)
        avg_eye_h = self._circular_mean_degrees([
            left_eye_lab_lch["H"],
            right_eye_lab_lch["H"],
        ])

        eye_l_diff = round(abs(left_eye_lab_lch["L"] - right_eye_lab_lch["L"]), 2)
        eye_a_diff = round(abs(left_eye_lab_lch["a"] - right_eye_lab_lch["a"]), 2)
        eye_b_diff = round(abs(left_eye_lab_lch["b"] - right_eye_lab_lch["b"]), 2)
        eye_c_diff = round(abs(left_eye_lab_lch["C"] - right_eye_lab_lch["C"]), 2)

        eye_h_diff_raw = abs(left_eye_lab_lch["H"] - right_eye_lab_lch["H"])
        eye_h_diff = round(min(eye_h_diff_raw, 360 - eye_h_diff_raw), 2)

        eye_vs_skin_l_diff = round(abs(avg_eye_l - skin_features["avg_skin_L"]), 2)
        eye_darkness = round(100 - avg_eye_l, 2)

        return {
            "avg_eye_r": avg_eye_r,
            "avg_eye_g": avg_eye_g,
            "avg_eye_b": avg_eye_b,

            "avg_eye_L": avg_eye_l,
            "avg_eye_a": avg_eye_a,
            "avg_eye_b_lab": avg_eye_b_lab,
            "avg_eye_C": avg_eye_c,
            "avg_eye_H": avg_eye_h,

            "eye_L_diff": eye_l_diff,
            "eye_a_diff": eye_a_diff,
            "eye_b_diff": eye_b_diff,
            "eye_C_diff": eye_c_diff,
            "eye_H_diff": eye_h_diff,

            "eye_vs_skin_L_diff": eye_vs_skin_l_diff,
            "eye_darkness": eye_darkness,
        }

    def _extract_region_color_summary(
        self,
        image: np.ndarray,
        region: dict[str, int],
        patch_validator: Callable[[np.ndarray], bool],
    ) -> dict[str, Any]:
        region_pixels = self._extract_region_pixels(image, region)
        patch_rgbs, patch_lab_lch = self._extract_valid_patch_features(region_pixels, patch_validator)

        if not patch_lab_lch:
            return {
                "success": False,
                "rgb": [0, 0, 0],
                "lab_lch": {"L": 0.0, "a": 0.0, "b": 0.0, "C": 0.0, "H": 0.0},
                "patch_count": 0,
            }

        return {
            "success": True,
            "rgb": self._mean_rgb_from_patch_list(patch_rgbs),
            "lab_lch": self._aggregate_patch_lab_lch(patch_lab_lch),
            "patch_count": len(patch_lab_lch),
        }

    def extract_color_features(
        self,
        image_path: str | Path,
        is_hair_visible: str = "yes",
        is_hair_natural: str = "yes",
        natural_hair_color: str | None = None,
    ) -> dict[str, Any]:
        image_path = str(image_path)

        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "error": "Image could not be loaded."
            }

        region_result = self.region_service.extract_regions(image_path)
        if not region_result.get("success"):
            return region_result

        regions = region_result["regions"]

        left_cheek = self._extract_region_color_summary(image, regions["left_cheek"], self._is_valid_skin_patch)
        right_cheek = self._extract_region_color_summary(image, regions["right_cheek"], self._is_valid_skin_patch)
        forehead = self._extract_region_color_summary(image, regions["forehead"], self._is_valid_skin_patch)

        if not left_cheek["success"] or not right_cheek["success"] or not forehead["success"]:
            return {
                "success": False,
                "error": "Not enough valid skin patches found in one or more face regions."
            }

        skin_features = self._build_skin_features(
            left_cheek["rgb"],
            right_cheek["rgb"],
            forehead["rgb"],
            left_cheek["lab_lch"],
            right_cheek["lab_lch"],
            forehead["lab_lch"],
        )

        left_eye = self._extract_region_color_summary(image, regions["left_eye"], self._is_valid_eye_patch)
        right_eye = self._extract_region_color_summary(image, regions["right_eye"], self._is_valid_eye_patch)

        eye_features = None
        if left_eye["success"] and right_eye["success"]:
            eye_features = self._build_eye_features(
                left_eye["rgb"],
                right_eye["rgb"],
                left_eye["lab_lch"],
                right_eye["lab_lch"],
                skin_features,
            )

        observed_hair_summary: dict[str, Any] = {
            "used_observed_hair": False,
            "hair_rgb": None,
            "hair_lab_lch": None,
            "hair_patch_count": 0,
            "natural_hair_color": natural_hair_color,
        }

        if is_hair_visible == "yes" and is_hair_natural == "yes":
            hair = self._extract_region_color_summary(image, regions["hair_region"], self._is_valid_generic_patch)
            if hair["success"]:
                observed_hair_summary = {
                    "used_observed_hair": True,
                    "hair_rgb": hair["rgb"],
                    "hair_lab_lch": hair["lab_lch"],
                    "hair_patch_count": hair["patch_count"],
                    "natural_hair_color": natural_hair_color,
                }

        return {
            "success": True,
            "face_box": region_result["face_box"],
            "regions": regions,
            "features": {
                "skin": {
                    "left_cheek_rgb": left_cheek["rgb"],
                    "right_cheek_rgb": right_cheek["rgb"],
                    "forehead_rgb": forehead["rgb"],
                    "left_cheek_lab_lch": left_cheek["lab_lch"],
                    "right_cheek_lab_lch": right_cheek["lab_lch"],
                    "forehead_lab_lch": forehead["lab_lch"],
                    "left_cheek_patch_count": left_cheek["patch_count"],
                    "right_cheek_patch_count": right_cheek["patch_count"],
                    "forehead_patch_count": forehead["patch_count"],
                    "total_valid_patch_count": (
                        left_cheek["patch_count"]
                        + right_cheek["patch_count"]
                        + forehead["patch_count"]
                    ),
                    "aggregated_features": skin_features,
                },
                "eyes": {
                    "left_eye_rgb": left_eye["rgb"],
                    "right_eye_rgb": right_eye["rgb"],
                    "left_eye_lab_lch": left_eye["lab_lch"],
                    "right_eye_lab_lch": right_eye["lab_lch"],
                    "left_eye_patch_count": left_eye["patch_count"],
                    "right_eye_patch_count": right_eye["patch_count"],
                    "aggregated_features": eye_features,
                },
                "hair": observed_hair_summary,
                "metadata": {
                    "is_hair_visible": is_hair_visible,
                    "is_hair_natural": is_hair_natural,
                    "natural_hair_color": natural_hair_color,
                }
            }
        }