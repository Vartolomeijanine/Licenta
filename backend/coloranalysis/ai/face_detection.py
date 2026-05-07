from __future__ import annotations

from pathlib import Path
from typing import Any

import cv2


class FaceDetectionService:
    def __init__(self) -> None:
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

    def detect_face(self, image_path: str | Path) -> dict[str, Any]:
        image_path = str(image_path)

        image = cv2.imread(image_path)
        if image is None:
            return {
                "success": False,
                "face_detected": False,
                "error": "Image could not be loaded."
            }

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.05,
            minNeighbors=3,
            minSize=(60, 60)
        )

        if len(faces) == 0:
            return {
                "success": True,
                "face_detected": False,
                "message": "No face detected."
            }

        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face

        return {
            "success": True,
            "face_detected": True,
            "message": "Face detected successfully.",
            "face_box": {
                "x": int(x),
                "y": int(y),
                "w": int(w),
                "h": int(h),
            }
        }