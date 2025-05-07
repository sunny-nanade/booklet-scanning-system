// static/js/camera.js

export async function startCamera(deviceId, resolution = "640x480") {
    const [width, height] = resolution.split("x").map(Number);
  
    const constraints = {
      video: {
        width,
        height,
        deviceId: deviceId ? { exact: deviceId } : undefined
      }
    };
  
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    const videoElement = document.getElementById("video");
    videoElement.srcObject = stream;
    return stream;
  }
  
  export function applyFlip(horizontal, vertical) {
    const video = document.getElementById("video");
    const scaleX = horizontal ? -1 : 1;
    const scaleY = vertical ? -1 : 1;
    video.style.transform = `scale(${scaleX}, ${scaleY})`;
  }
  
  export function stopCamera() {
    const video = document.getElementById("video");
    const stream = video.srcObject;
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      video.srcObject = null;
    }
  }
  