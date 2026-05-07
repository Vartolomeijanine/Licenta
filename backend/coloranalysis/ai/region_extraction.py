from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2

from coloranalysis.ai.face_detection import FaceDetectionService


class RegionExtractionService:
    def __init__(self) -> None:
        self.face_detector = FaceDetectionService()

    def extract_regions(self, image_path: str | Path) -> dict[str, Any]:
        image_path = str(image_path)

        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "error": "Image could not be loaded."
            }

        detection_result = self.face_detector.detect_face(image_path)

        if not detection_result.get("face_detected"):
            return {
                "success": False,
                "error": "No face detected."
            }

        face_box = detection_result["face_box"]
        x = face_box["x"]
        y = face_box["y"]
        w = face_box["w"]
        h = face_box["h"]

        img_h, img_w = image.shape[:2]

        def clamp_region(x1: int, y1: int, x2: int, y2: int) -> dict[str, int]:
            x1 = max(0, min(x1, img_w - 1))
            y1 = max(0, min(y1, img_h - 1))
            x2 = max(0, min(x2, img_w))
            y2 = max(0, min(y2, img_h))

            return {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
            }

        # skin regions
        left_cheek = clamp_region(
            x + int(w * 0.18),
            y + int(h * 0.52),
            x + int(w * 0.38),
            y + int(h * 0.72),
        )

        right_cheek = clamp_region(
            x + int(w * 0.62),
            y + int(h * 0.52),
            x + int(w * 0.82),
            y + int(h * 0.72),
        )

        forehead = clamp_region(
            x + int(w * 0.35),
            y + int(h * 0.15),
            x + int(w * 0.65),
            y + int(h * 0.30),
        )

        # eye regions
        # eye regions - smaller and more centered
        left_eye = clamp_region(
            x + int(w * 0.27),
            y + int(h * 0.37),
            x + int(w * 0.37),
            y + int(h * 0.43),
        )

        right_eye = clamp_region(
            x + int(w * 0.63),
            y + int(h * 0.37),
            x + int(w * 0.73),
            y + int(h * 0.43),
        )

        # hair region: upper band around hairline / top head area
        hair_region = clamp_region(
            x + int(w * 0.15),
            y,
            x + int(w * 0.85),
            y + int(h * 0.18),
        )

        return {
            "success": True,
            "face_box": face_box,
            "regions": {
                "left_cheek": left_cheek,
                "right_cheek": right_cheek,
                "forehead": forehead,
                "left_eye": left_eye,
                "right_eye": right_eye,
                "hair_region": hair_region,
            }
        }