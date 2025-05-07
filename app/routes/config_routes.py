from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
import json
import os

router = APIRouter()
CONFIG_FILE = "config.json"

def read_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def write_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

@router.get("/get-config")
def get_config():
    config = read_config()
    return JSONResponse(config)

@router.post("/save-config")
async def save_config(request: Request):
    form = await request.form()
    config = {
        "cameraId": form.get("cameraId"),
        "flipH": form.get("flipH") == "true",
        "flipV": form.get("flipV") == "true",
        "main_pages": int(form.get("main_pages", 18)),
        "supplement_page_count": int(form.get("supplement_page_count", 4)),
        "leftCrop": json.loads(form.get("leftCrop", "[0,0,0,0]")),
        "rightCrop": json.loads(form.get("rightCrop", "[0,0,0,0]"))
    }
    write_config(config)
    return JSONResponse({"status": "saved"})
