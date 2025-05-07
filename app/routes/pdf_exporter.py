from fastapi import APIRouter
from fastapi.responses import FileResponse, JSONResponse
from PIL import Image
import os
import glob

router = APIRouter()

# 📥 Manual PDF export (download link endpoint)
@router.get("/export-pdf/{session_name}")
def export_pdf(session_name: str):
    image_folder = os.path.join("scans", "main", session_name)
    output_pdf = os.path.join("scans", "main", f"{session_name}.pdf")

    try:
        image_paths = sorted(glob.glob(os.path.join(image_folder, "page_*.jpg")))
        if not image_paths:
            return JSONResponse({"error": "No scanned pages found."}, status_code=404)

        images = [Image.open(p).convert("RGB") for p in image_paths]
        images[0].save(output_pdf, save_all=True, append_images=images[1:])

        return FileResponse(output_pdf, media_type="application/pdf", filename=os.path.basename(output_pdf))

    except Exception as e:
        print(f"❌ Error exporting PDF: {e}")
        return JSONResponse({"error": "Failed to generate PDF."}, status_code=500)


# ⚙️ Auto-generate PDF (triggered from JS)
@router.post("/generate-pdf")
def generate_pdf():
    base_path = os.path.join("scans", "main")

    try:
        # Sort by name (timestamped folders) to get the latest session
        subdirs = sorted(
            [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        )
        if not subdirs:
            return JSONResponse({"status": "error", "message": "No scan folders found."}, status_code=404)

        latest_session = subdirs[-1]
        image_folder = os.path.join(base_path, latest_session)
        output_pdf = os.path.join(base_path, f"{latest_session}.pdf")

        image_paths = sorted(glob.glob(os.path.join(image_folder, "page_*.jpg")))
        if not image_paths:
            return JSONResponse({"status": "error", "message": "No scanned pages found."}, status_code=404)

        images = [Image.open(p).convert("RGB") for p in image_paths]
        images[0].save(output_pdf, save_all=True, append_images=images[1:])

        return JSONResponse({"status": "success", "filename": os.path.basename(output_pdf)})

    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return JSONResponse({"status": "error", "message": "PDF generation failed."}, status_code=500)
