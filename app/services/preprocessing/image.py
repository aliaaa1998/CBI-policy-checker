from pathlib import Path

import cv2
import numpy as np


def preprocess_image(src: Path, dst: Path) -> Path:
    image = cv2.imread(str(src))
    if image is None:
        raise ValueError(f"Cannot load image: {src}")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    denoise = cv2.fastNlMeansDenoising(gray, h=10)
    thresh = cv2.adaptiveThreshold(denoise, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
    coords = np.column_stack(np.where(thresh < 200))
    if len(coords) > 10:
        angle = cv2.minAreaRect(coords)[-1]
        angle = -(90 + angle) if angle < -45 else -angle
        (h, w) = thresh.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        thresh = cv2.warpAffine(thresh, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    cv2.imwrite(str(dst), thresh)
    return dst
