// static/js/overlay.js

export function drawOverlay(ctx, data = {}) {
  ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height);

  const { canvas } = ctx;

  // Always draw a default green centerline
  const midX = canvas.width / 2;
  ctx.strokeStyle = "lime";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(midX, 0);
  ctx.lineTo(midX, canvas.height);
  ctx.stroke();

  ctx.font = "14px Arial";
  ctx.fillStyle = "lime";
  ctx.fillText("Split Line", midX + 5, 20);

  // Optional QR code box
  if (data.qr) {
    const { x, y, width, height } = data.qr;
    ctx.strokeStyle = "lime";
    ctx.lineWidth = 3;
    ctx.strokeRect(x, y, width, height);
    if (data.qr_data) {
      ctx.font = "16px Arial";
      ctx.fillStyle = "lime";
      ctx.fillText(`QR: ${data.qr_data}`, x, y - 10);
    }
  }

  // Optional Booklet outline
  if (data.booklet && data.booklet.length === 4) {
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(data.booklet[0][0], data.booklet[0][1]);
    for (let i = 1; i < 4; i++) {
      ctx.lineTo(data.booklet[i][0], data.booklet[i][1]);
    }
    ctx.closePath();
    ctx.stroke();

    ctx.font = "16px Arial";
    ctx.fillStyle = "white";
    ctx.fillText(`Booklet detected`, data.booklet[0][0], data.booklet[0][1] - 10);
  }

  // Optional Midline from detection logic (if used later)
  if (data.midline && data.midline.length === 2) {
    const pt1 = data.midline[0];
    const pt2 = data.midline[1];
    ctx.strokeStyle = "green";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(pt1[0], pt1[1]);
    ctx.lineTo(pt2[0], pt2[1]);
    ctx.stroke();

    ctx.font = "14px Arial";
    ctx.fillStyle = "green";
    ctx.fillText("Split Line", pt1[0], pt1[1] - 10);
  }
}
