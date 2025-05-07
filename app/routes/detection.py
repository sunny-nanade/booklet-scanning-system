from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import numpy as np
import cv2
from pyzbar.pyzbar import decode
from PIL import Image
import io

router = APIRouter()
qr_lock = None  # Holds detected QR persistently

@router.post("/process-frame")
async def process_frame(frame: UploadFile = File(...)):
    global qr_lock
    result = {
        "qr": None,
        "qr_data": None,
        "booklet": None,
        "midline": None
    }

    try:
        contents = await frame.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        frame_np = np.array(image)

        # QR Code Detection
        qr_codes = decode(frame_np)
        if qr_codes and qr_lock is None:
            qr = qr_codes[0]
            (x, y, w, h) = qr.rect
            qr_lock = qr.data.decode("utf-8")
            result["qr"] = {"x": x, "y": y, "width": w, "height": h}
            result["qr_data"] = qr_lock
        elif qr_lock:
            result["qr_data"] = qr_lock

        # Booklet detection
        gray = cv2.cvtColor(frame_np, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                       cv2.THRESH_BINARY_INV, 51, 10)
        kernel = np.ones((7, 7), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(cleaned, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        h, w = gray.shape
        min_area = 0.1 * w * h
        max_area = 0.9 * w * h

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < min_area or area > max_area:
                continue

            rect = cv2.minAreaRect(cnt)
            box = cv2.boxPoints(rect)
            box = np.intp(box)
            box = sorted(box, key=lambda p: (p[1], p[0]))
            top = sorted(box[:2], key=lambda p: p[0])
            bottom = sorted(box[2:], key=lambda p: p[0])
            pts = [top[0], top[1], bottom[1], bottom[0]]

            result["booklet"] = [[int(p[0]), int(p[1])] for p in pts]

            # Midline calculation
            mid_x1 = int((pts[0][0] + pts[3][0]) / 2)
            mid_y1 = int((pts[0][1] + pts[3][1]) / 2)
            mid_x2 = int((pts[1][0] + pts[2][0]) / 2)
            mid_y2 = int((pts[1][1] + pts[2][1]) / 2)
            result["midline"] = [[mid_x1, mid_y1], [mid_x2, mid_y2]]
            break

        return JSONResponse(result)
    except Exception as e:
        print(f"❌ Error processing frame: {e}")
        return JSONResponse({"error": "Failed to process frame"}, status_code=500)


@router.post("/reset-qr")
async def reset_qr():
    global qr_lock
    qr_lock = None
    return {"status": "QR reset"}


# ✅ NEW: Minimal QR detection endpoint for first-page filename
@router.post("/detect-qr")
async def detect_qr(frame: UploadFile = File(...)):
    try:
        contents = await frame.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        frame_np = np.array(image)

        qr_codes = decode(frame_np)
        if qr_codes:
            qr_data = qr_codes[0].data.decode("utf-8")
            return {"found": True, "value": qr_data}
        else:
            return {"found": False, "value": None}
    except Exception as e:
        print(f"❌ QR detection error: {e}")
        return {"found": False, "value": None}
