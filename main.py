import os
import sys
import shutil
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse

from app.routes.detection import router as detection_router
from app.routes.scan_flow import router as scan_flow_router
from app.routes.pdf_exporter import router as pdf_exporter_router
from app.routes.config_routes import router as config_router

# 📦 Support PyInstaller --onefile path resolution
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

app = FastAPI()

# Ensure folders exist before mounting
required_dirs = ["static", "scans", "scans/main", "templates"]
for folder in required_dirs:
    path = BASE_DIR / folder
    path.mkdir(parents=True, exist_ok=True)

# Mount static folders
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/scans", StaticFiles(directory=BASE_DIR / "scans"), name="scans")


# Templates
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Routers
app.include_router(detection_router)
app.include_router(scan_flow_router)
app.include_router(pdf_exporter_router)
app.include_router(config_router)

# ✅ Optional: Clean up on startup
@app.on_event("startup")
async def clear_old_scans():
    scan_dir = BASE_DIR / "scans" / "main"
    if scan_dir.exists():
        for folder in scan_dir.iterdir():
            if folder.is_dir():
                shutil.rmtree(folder)
        print("🧹 Old scans cleared on startup")
    scan_dir.mkdir(parents=True, exist_ok=True)

# Pages
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/scan", response_class=HTMLResponse)
async def scan(request: Request):
    return templates.TemplateResponse("scan.html", {"request": request})

@app.get("/config", response_class=HTMLResponse)
async def config(request: Request):
    return templates.TemplateResponse("config.html", {"request": request})

# ✅ Manual cleanup endpoint
@app.post("/cleanup-scans")
async def cleanup_scans():
    scan_dir = BASE_DIR / "scans" / "main"
    if scan_dir.exists():
        for folder in scan_dir.iterdir():
            if folder.is_dir():
                shutil.rmtree(folder)
        return JSONResponse({"status": "cleared"})
    return JSONResponse({"status": "no_folders"})

# ✅ Reset full session — folders + PDFs
@app.post("/reset-session")
async def reset_session():
    scan_dir = BASE_DIR / "scans" / "main"
    if scan_dir.exists():
        # Collect all PDFs
        pdfs = sorted([p for p in scan_dir.glob("*.pdf")], key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Keep latest 2, delete rest
        for old_pdf in pdfs[2:]:
            old_pdf.unlink()

        # Clean all scan folders
        for item in scan_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item)

    scan_dir.mkdir(parents=True, exist_ok=True)
    return JSONResponse({"status": "reset"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
