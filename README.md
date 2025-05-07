# 📘 Booklet Scanning System

This is a modular Python-based application developed to streamline the academic digitization process. It captures high-resolution scans of booklets using a custom-built foldable acrylic structure with a mounted Logitech Brio MX camera. The system supports QR code detection, automatic page splitting, PDF generation, and is designed for future integration with intelligent agents for tracking and automation.

---

## 🚀 Features

- Real-time camera preview with alignment guides  
- QR code detection to auto-name scanned files  
- Automated left/right page splitting from camera feed  
- Instant PDF generation from scanned images  
- Configurable crop zones and camera resolution  
- Lightweight Python backend using FastAPI  
- Future-ready for handwriting recognition and AI-based agents  

---

## 🛠 Technologies Used

- Python 3.10+  
- FastAPI – backend web framework  
- Uvicorn – ASGI server  
- OpenCV – image capture and processing  
- PyMuPDF – PDF generation  
- jsQR – browser-side QR code detection  
- Tesseract OCR (planned)  
- HTML, CSS, JavaScript – frontend interface  

---

## 🧪 How to Set Up and Run the App (All Steps Inline)

1. **Clone the Repository and Set Up the Environment**

```bash
git clone https://github.com/sunny-nanade/booklet-scanning-system.git
cd booklet-scanning-system
```

2. **Create a Virtual Environment**

```bash
python -m venv venv
```

3. **Activate the Environment**

On **Windows**:

```bash
.\venv\Scripts\activate
```

On **macOS/Linux**:

```bash
source venv/bin/activate
```

4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

5. **Run the App**

```bash
uvicorn main:app --reload
```

Then open your browser and go to:  
http://127.0.0.1:8000

---

## 📖 How It Works

- Use the live camera preview to align the booklet  
- QR code is auto-detected to name the output file  
- Press the spacebar to scan a page spread (left & right)  
- Scanned pages are cropped and added to a PDF  
- Preview scanned pages and download the final PDF when done  

---

## 📁 Folder Structure

```
booklet-scanning-system/
├── main.py                 # FastAPI app entry point
├── templates/              # HTML pages (scan, config, login)
├── static/                 # JavaScript, CSS, overlays
├── scans/                  # Temporary scan images
├── output/                 # Final PDF files
├── config.json             # Crop zones, resolution, page logic
├── requirements.txt        # Python dependencies
├── LICENSE.txt             # Custom license terms
└── README.md               # This file
```

---

## 📸 Hardware Setup

- Camera: Logitech Brio MX (4K, top-mounted)  
- Structure: Custom foldable acrylic frame (SolidWorks-designed)  
- Lighting: LED strips for even illumination  
- Background: White booklet placed on black chart paper for clean contrast  

---

## 🔒 License

```
Copyright © 2025 Sunny Nanade

This software is proprietary and confidential. No part of this codebase may be used, copied, modified, or distributed without explicit written permission from the author.

For usage inquiries, contact: sunny.nanade@nmims.edu
```

---

## 🙌 Acknowledgment

This tool was developed as part of an academic digitization initiative integrating physical system design, AI-ready scanning workflows, and modular automation for scalable booklet processing in educational institutions.
