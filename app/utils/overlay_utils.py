import cv2

def draw_qr_overlay(frame, qr_data, qr_box):
    """Draws a green box with QR data label on the frame."""
    if qr_box:
        x, y, w, h = qr_box["x"], qr_box["y"], qr_box["width"], qr_box["height"]
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        if qr_data:
            cv2.putText(frame, f"QR: {qr_data}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

def draw_booklet_outline(frame, points):
    """Draws a white polygon around the booklet area."""
    if points and len(points) == 4:
        pts = [(int(p[0]), int(p[1])) for p in points]
        for i in range(4):
            cv2.line(frame, pts[i], pts[(i + 1) % 4], (255, 255, 255), 2)
        cv2.putText(frame, "Booklet detected", (pts[0][0], pts[0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def draw_midline(frame, midline_pts):
    """Draws a green vertical line to indicate the split between pages."""
    if midline_pts:
        pt1 = tuple(midline_pts[0])
        pt2 = tuple(midline_pts[1])
        cv2.line(frame, pt1, pt2, (0, 255, 0), 2)
        cv2.putText(frame, "Split Line", (pt1[0], pt1[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
