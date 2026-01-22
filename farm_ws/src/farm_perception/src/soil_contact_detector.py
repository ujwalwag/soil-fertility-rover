"""Soil contact detection using vision."""

import cv2
import numpy as np


def check_soil_contact(cv_image: np.ndarray, contact_threshold: float = 0.5) -> bool:
    """Detect soil-colored regions and return True if contact threshold exceeded."""
    hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
    lower = np.array([10, 50, 50])
    upper = np.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower, upper)
    h, w = mask.shape
    center = mask[h // 4 : 3 * h // 4, w // 4 : 3 * w // 4]
    pct = np.sum(center > 0) / max(1, center.size)
    return pct > contact_threshold
