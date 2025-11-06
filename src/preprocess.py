import cv2
import numpy as np

def preprocess(bgr):
    img = bgr.copy()
    h, w = img.shape[:2]
    scale = 1600 / max(h, w) if max(h, w) < 1600 else 1.0
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 7, 40, 40)
    gray = cv2.convertScaleAbs(gray, alpha=1.25, beta=8)

    binimg = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 10
    )
    return binimg

def preprocess_both(bgr):
    a = preprocess(bgr)
    b = cv2.bitwise_not(a)
    return [a, b]
