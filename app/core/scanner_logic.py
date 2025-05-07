# app/core/scanner_logic.py

import cv2
import numpy as np
import os
from datetime import datetime


def generate_filename(qr_value=None):
    if qr_value:
        return qr_value
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir_exists(path):
    os.makedirs(path, exist_ok=True)


def split_spread(image, flip_first_last=False, is_first=False, is_last=False):
    h, w = image.shape[:2]
    mid_x = w // 2

    left_page = image[:, :mid_x]
    right_page = image[:, mid_x:]

    if is_first:
        return (right_page, None) if not flip_first_last else (None, left_page)
    elif is_last:
        return (left_page, None) if not flip_first_last else (None, right_page)
    else:
        return left_page, right_page


def save_pages_as_images(left, right, folder, page_start):
    saved_paths = []
    if left is not None:
        path_left = os.path.join(folder, f"page_{page_start:02d}.jpg")
        cv2.imwrite(path_left, left)
        saved_paths.append(path_left)
    if right is not None:
        path_right = os.path.join(folder, f"page_{page_start + 1:02d}.jpg")
        cv2.imwrite(path_right, right)
        saved_paths.append(path_right)
    return saved_paths