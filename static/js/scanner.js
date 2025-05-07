// static/js/scanner.js

let currentPage = 1;
let scannedPages = [];
let supplementCount = 0;
let supplementPages = 4; // default
let qrLocked = false;
let filenameFromQR = null;

// ✅ Update supplement count on selection
function updateSupplementCount() {
  const selected = document.querySelector('input[name="supplementCount"]:checked');
  supplementCount = selected ? parseInt(selected.value) : 0;
}

document.querySelectorAll('input[name="supplementCount"]').forEach(radio => {
  radio.addEventListener('change', updateSupplementCount);
});
updateSupplementCount();

// ✅ Capture image on spacebar press (actual listener is in main.js)
export function captureSpread() {
  const video = document.getElementById("video");
  if (!video || !video.videoWidth) return;

  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  canvas.toBlob(blob => {
    const formData = new FormData();
    formData.append("spread", blob);
    formData.append("pageStart", currentPage);
    formData.append("qrValue", filenameFromQR || "");

    fetch("/scan-spread", {
      method: "POST",
      body: formData,
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === "scanned" && Array.isArray(data.pages)) {
          scannedPages.push(...data.pages);
          currentPage += data.pages.length;
          renderPreviews();
        }
      })
      .catch(err => console.error("❌ Error scanning spread:", err));
  }, "image/jpeg");
}

// ✅ Render thumbnail previews
function renderPreviews() {
  const container = document.getElementById("previewContainer");
  container.innerHTML = "";
  scannedPages.forEach((page, index) => {
    const div = document.createElement("div");
    div.className = "preview-thumb";
    const img = document.createElement("img");
    img.src = page.url || page; // support string or object
    const label = document.createElement("p");
    label.textContent = `Page ${index + 1}`;
    div.appendChild(img);
    div.appendChild(label);
    container.appendChild(div);
  });
}

// ✅ Used when QR is detected externally
export function setQRValue(value) {
  qrLocked = true;
  filenameFromQR = value;
}
