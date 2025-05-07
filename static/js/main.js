console.log("📷 main.js loaded");

import { startCamera, applyFlip } from "./camera.js";
import { addPagePreview, clearPreviews } from "./preview.js";

let stream = null;
let config = null;
let filenameFromQR = null;
let scannedPages = [];
let savedPageCounter = 1;
let isScanning = false;
let supplementSelector = null;
let qrDetected = false;

async function initCameraAndEvents() {
  resetFrontendState();

  supplementSelector = document.getElementById('supplementCount');
  config = JSON.parse(localStorage.getItem("cameraConfig"));

  await resetSession();
  console.log("🔄 Session reset on page load");

  if (!config || !config.cameraId) {
    alert("No camera configuration found. Please visit the Config page first.");
    window.location.href = "/config";
    return;
  }

  try {
    stream = await startCamera(config.cameraId, config.resolution || "640x480");
    applyFlip(config.flipH, config.flipV);
    console.log("✅ Camera started");

    const video = document.getElementById("video");
    video.addEventListener("playing", () => {
      console.log("🎥 Video playing — starting overlay");
      loopOverlayUpdate();
    }, { once: true });

    setupSpacebarHandler();
    startQRDetectionLoop();

    window.resetQR = function () {
      if (isScanning) return;
      fetch('/reset-qr', { method: 'POST' })
        .then(() => {
          console.log("✅ QR lock reset.");
          qrDetected = false;
          filenameFromQR = null;
          startQRDetectionLoop();
        })
        .catch(err => {
          console.error("QR reset failed:", err);
        });
    };

    document.body.focus();
  } catch (err) {
    console.error("❌ Error accessing camera:", err);
    alert("Camera access failed.");
  }
}

function resetFrontendState() {
  scannedPages = [];
  savedPageCounter = 1;
  filenameFromQR = null;
  isScanning = false;
  qrDetected = false;

  clearPreviews();
  const statusText = document.getElementById("statusText");
  if (statusText) {
    statusText.textContent = "Ready to scan";
  }
}

async function resetSession() {
  try {
    const response = await fetch("/reset-session", { method: "POST" });
    if (!response.ok) throw new Error("Failed to reset backend session");
    resetFrontendState();
  } catch (err) {
    console.error("❌ Session reset error:", err);
    alert("Session reset failed. Please refresh the page.");
  }
}

function loopOverlayUpdate() {
  const video = document.getElementById("video");
  const canvas = document.getElementById("overlayCanvas");
  const ctx = canvas.getContext("2d");

  function draw() {
    if (!video.videoWidth || !video.videoHeight) {
      requestAnimationFrame(draw);
      return;
    }

    if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
    }

    console.log("🎨 Drawing overlay with canvas size:", canvas.width, canvas.height);
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    const midX = canvas.width / 2;
    ctx.strokeStyle = "lime";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(midX, 0);
    ctx.lineTo(midX, canvas.height);
    ctx.stroke();

    ctx.font = "bold 20px Arial";
    ctx.fillStyle = "lime";
    ctx.fillText("CENTRE LINE", midX + 10, 30);

    requestAnimationFrame(draw);
  }

  draw();
}

function startQRDetectionLoop() {
  const statusText = document.getElementById("statusText");
  const video = document.getElementById("video");

  const interval = setInterval(async () => {
    if (qrDetected || isScanning || scannedPages.length > 0) {
      clearInterval(interval);
      return;
    }

    if (!video.videoWidth || !video.videoHeight) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/jpeg', 1.0);
    });

    const formData = new FormData();
    formData.append('frame', blob);

    try {
      const res = await fetch('/detect-qr', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (data.found && data.value) {
        filenameFromQR = data.value;
        qrDetected = true;
        statusText.textContent = `✅ QR Detected: ${filenameFromQR}`;
        console.log("✅ QR Detected:", filenameFromQR);
        clearInterval(interval);
      } else {
        console.log("⌛ QR not yet detected...");
      }

    } catch (err) {
      console.error("❌ QR detection error:", err);
    }

  }, 250);
}

async function captureSpread() {
  if (isScanning) return;

  isScanning = true;
  supplementSelector.disabled = true;
  document.getElementById('resetQRBtn').disabled = true;

  console.log("📸 Capture started");
  const statusText = document.getElementById("statusText");
  const video = document.getElementById("video");

  try {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise((resolve) => {
      canvas.toBlob(resolve, 'image/jpeg', 0.9);
    });

    if (!filenameFromQR) {
      const now = new Date();
      filenameFromQR = now.toISOString().replace(/[:.]/g, '-');
      statusText.textContent = `⚠️ QR not detected. Using: ${filenameFromQR}`;
    }

    qrDetected = true;

    const formData = new FormData();
    formData.append('frame', blob);
    formData.append('pageStart', savedPageCounter);
    formData.append('qrValue', filenameFromQR);
    formData.append('supplementCount', supplementSelector.value);

    const res = await fetch('/scan-spread', {
      method: 'POST',
      body: formData
    });

    const data = await res.json();

    if (data.status === "error" && data.error.includes("already completed")) {
      await resetSession();
      statusText.textContent = "Session was completed. Ready to start new scan.";
      return;
    }

    if (data.status === "scanned") {
      let startPage = savedPageCounter;

      for (const url of data.pages) {
        const pageNum = savedPageCounter;
        try {
          const response = await fetch(url);
          const blob = await response.blob();
          addPagePreview(blob, pageNum);
          savedPageCounter++;
        } catch (err) {
          console.error("Preview load failed:", err);
        }
      }

      scannedPages = [...scannedPages, ...data.pages];
      const endPage = savedPageCounter - 1;
      statusText.textContent = `✅ Scan successful! (Page ${startPage}-${endPage})`;

      if (data.done) {
        setTimeout(() => {
          finishBooklet();
        }, 400);
      }
    } else {
      throw new Error(data.error || "Scan failed");
    }
  } catch (err) {
    console.error("❌ Scan failed:", err);
    statusText.textContent = `❌ Scan failed: ${err.message}`;
    await resetSession();
  } finally {
    isScanning = false;
    supplementSelector.disabled = false;
    document.getElementById('resetQRBtn').disabled = false;
  }
}

function setupSpacebarHandler() {
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space' &&
      e.target.tagName !== 'INPUT' &&
      e.target.tagName !== 'TEXTAREA' &&
      !e.target.isContentEditable) {
      e.preventDefault();
      console.log("⏎ Spacebar pressed - scanning...");
      captureSpread();
    }
  }, { capture: true });
}

async function finishBooklet() {
  const statusText = document.getElementById("statusText");

  try {
    const res = await fetch("/generate-pdf", { method: "POST" });
    const data = await res.json();

    if (data.status === "success") {
      const pdfUrl = `/export-pdf/${data.filename.replace(".pdf", "")}`;
      const a = document.createElement("a");
      a.href = pdfUrl;
      a.download = data.filename;
      document.body.appendChild(a);
      a.click();
      a.remove();

      statusText.textContent = "✅ PDF downloaded automatically.";
      console.log("📄 PDF auto-downloaded:", pdfUrl);

      setTimeout(() => {
        resetSession();
        startQRDetectionLoop();
      }, 1000);
    } else {
      throw new Error("PDF generation failed");
    }
  } catch (err) {
    console.error("❌ Finish failed:", err);
    alert("Error during finalization.");
  }
}

window.addEventListener("DOMContentLoaded", initCameraAndEvents);
