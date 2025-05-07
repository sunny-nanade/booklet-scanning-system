import cv2
import numpy as np

def crop_page(image, crop_box):
    x, y, w, h = crop_box
    return image[y:y+h, x:x+w]

def trim_black_borders(image, threshold=10):
    """Trims black borders around a page using a brightness threshold."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image  # nothing to trim

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    return image[y:y+h, x:x+w]

def resize_page(image, target_size=(1200, 1600)):
    return cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

def split_spread(image, midline=None, config=None):
    """Splits a scanned spread into left and right pages."""
    h, w, _ = image.shape

    if midline:
        x1 = int((midline[0][0] + midline[1][0]) / 2)
    else:
        x1 = w // 2  # fallback to vertical center

    # Use configured crop areas if present
    if config and "leftCrop" in config and "rightCrop" in config:
        left = crop_page(image, config["leftCrop"])
        right = crop_page(image, config["rightCrop"])
    else:
        left = image[:, :x1]
        right = image[:, x1:]

    return left, right
