from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


_FACE_CASCADE = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


def _blur_region(image: np.ndarray, x: int, y: int, w: int, h: int) -> None:
    roi = image[y : y + h, x : x + w]
    blurred = cv2.GaussianBlur(roi, (51, 51), 0)
    image[y : y + h, x : x + w] = blurred


def _mask_lower_band(image: np.ndarray) -> bool:
    height, width = image.shape[:2]
    band_start = int(height * 0.45)
    band_height = int(height * 0.18)
    _blur_region(image, 0, band_start, width, band_height)
    return True


def mask_sensitive_regions(image: np.ndarray) -> Tuple[np.ndarray, bool]:
    """Blur faces and ID bands to comply with PDPA."""

    masked = image.copy()
    is_masked = False

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = _FACE_CASCADE.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    for (x, y, w, h) in faces:
        _blur_region(masked, x, y, w, h)
        is_masked = True

    if _mask_lower_band(masked):
        is_masked = True

    return masked, is_masked
