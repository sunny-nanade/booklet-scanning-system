# app/routes/scan_flow.py
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
import json
import numpy as np
from datetime import datetime
from PIL import Image
import io
import traceback
from pathlib import Path
import shutil

router = APIRouter()

scan_state = {
    "filename": None,
    "scan_count": 0,
    "main_page_count": 0,
    "supplement_count": 0,
    "save_dir": None,
    "current_page": 1,
    "total_scans": 0,
    "phase": "main",
    "current_supplement": 0,
    "main_pages_scanned": 0,
    "supplement_pages_scanned": 0,
    "total_supplements": 0
}

def reset_scan_state():
    """Completely reset the scan state to initial values"""
    global scan_state
    # Clear the scan directory if it exists
    if scan_state["save_dir"] and scan_state["save_dir"].exists():
        try:
            if scan_state["save_dir"].is_dir():
                shutil.rmtree(scan_state["save_dir"])
        except Exception as e:
            print(f"⚠️ Could not remove directory {scan_state['save_dir']}: {e}")
    
    scan_state.update({
        "filename": None,
        "scan_count": 0,
        "main_page_count": 0,
        "supplement_count": 0,
        "save_dir": None,
        "current_page": 1,
        "total_scans": 0,
        "phase": "main",
        "current_supplement": 0,
        "main_pages_scanned": 0,
        "supplement_pages_scanned": 0,
        "total_supplements": 0
    })

@router.post("/reset-session")
async def reset_session():
    """Endpoint to completely reset the scanning session"""
    reset_scan_state()
    return JSONResponse({"status": "reset", "message": "Scan session reset successfully"})

@router.post("/scan-spread")
async def scan_spread(
    request: Request,
    frame: UploadFile = File(...),
    pageStart: int = Form(...),
    qrValue: str = Form(''),
    supplementCount: int = Form(0)
):
    try:
        MAIN_PAGES = 32
        SUPPLEMENT_PAGES_PER_BOOKLET = 4
        total_supplements = min(int(supplementCount), 9)
        total_main_scans = 17
        total_supp_scans = total_supplements * 3
        total_scans = total_main_scans + total_supp_scans

        # Reset if scan_count is 0 but save_dir already exists (dirty state)
        if scan_state["scan_count"] == 0:
            if scan_state["save_dir"] and scan_state["save_dir"].exists():
                print("⚠️ Found old save_dir while scan_count=0. Forcing state reset.")
                reset_scan_state()

            scan_state.update({
                "filename": qrValue or datetime.now().strftime("%Y%m%d_%H%M%S"),
                "save_dir": Path(f"scans/main/{qrValue or datetime.now().strftime('%Y%m%d_%H%M%S')}"),
                "current_page": 1,
                "total_scans": total_scans,
                "phase": "main",
                "current_supplement": 0,
                "main_pages_scanned": 0,
                "supplement_pages_scanned": 0,
                "total_supplements": total_supplements
            })

        # Guard: stop if already done
        if scan_state["scan_count"] >= scan_state["total_scans"] and scan_state["scan_count"] > 0:
            return JSONResponse({
                "status": "error",
                "error": "Scan session already completed. Please reset the session.",
                "done": True
            }, status_code=400)

        # Ensure scan directory exists
        scan_state["save_dir"].mkdir(parents=True, exist_ok=True)

        # Read and split the image
        contents = await frame.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        img_np = np.array(image)
        mid_x = img_np.shape[1] // 2
        left = img_np[:, :mid_x]
        right = img_np[:, mid_x:]

        pages_to_save = []
        page_numbers = []

        if scan_state["phase"] == "main":
            if scan_state["scan_count"] == 0:
                pages_to_save = [right]
                page_numbers = [1]
                scan_state["current_page"] += 1
            elif scan_state["current_page"] >= MAIN_PAGES:
                pages_to_save = [left]
                page_numbers = [MAIN_PAGES]
                if scan_state["total_supplements"] > 0:
                    scan_state["phase"] = "supplement"
                    scan_state["current_page"] = 1
                    scan_state["current_supplement"] = 1
            else:
                pages_to_save = [left, right]
                page_numbers = [scan_state["current_page"], scan_state["current_page"] + 1]
                scan_state["current_page"] += 2
        else:
            current_supplement = scan_state["current_supplement"]
            supplement_offset = (current_supplement - 1) * SUPPLEMENT_PAGES_PER_BOOKLET

            if scan_state["current_page"] == 1:
                pages_to_save = [right]
                page_numbers = [1 + supplement_offset]
                scan_state["current_page"] += 1
            elif scan_state["current_page"] >= SUPPLEMENT_PAGES_PER_BOOKLET:
                pages_to_save = [left]
                page_numbers = [SUPPLEMENT_PAGES_PER_BOOKLET + supplement_offset]
                if current_supplement < scan_state["total_supplements"]:
                    scan_state["current_supplement"] += 1
                    scan_state["current_page"] = 1
            else:
                pages_to_save = [left, right]
                page_numbers = [
                    scan_state["current_page"] + supplement_offset,
                    scan_state["current_page"] + 1 + supplement_offset
                ]
                scan_state["current_page"] += 2

        # Save image pages
        filenames = []
        for page, page_num in zip(pages_to_save, page_numbers):
            img = Image.fromarray(page)
            file_num = page_num if scan_state["phase"] == "main" else MAIN_PAGES + page_num
            filename = scan_state["save_dir"] / f"page_{file_num:02}.jpg"
            filename.parent.mkdir(parents=True, exist_ok=True)
            img.save(str(filename), quality=70)
            filenames.append(f"/{filename.as_posix()}")

        scan_state["scan_count"] += 1
        done = scan_state["scan_count"] >= total_scans

        return JSONResponse({
            "status": "scanned",
            "pages": filenames,
            "current_scan": scan_state["scan_count"],
            "total_scans": total_scans,
            "page_numbers": page_numbers,
            "done": done
        })

    except Exception as e:
        print("❌ ERROR during scan-spread:")
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"{type(e).__name__}: {str(e)}"})
