from ultralytics import YOLO
import cv2
import time
import os
import sys

# ==============================
# PARAMETERS
# ==============================
MODEL_PATH = "models/yolov8n_identification_signals.pt"
CAMERA_INDEX = 0
IMG_SIZE = 640
CONF_THRESHOLD = 0.25

# ==============================
# CHECK MODEL EXISTS
# ==============================
if not os.path.exists(MODEL_PATH):
    print(f"Model not found: {MODEL_PATH}")
    sys.exit(1)

# ==============================
# LOAD MODEL
# ==============================
model = YOLO(MODEL_PATH)

# ==============================
# OPEN CAMERA
# ==============================
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("Error: camera could not be opened")
    sys.exit(1)

print("Camera opened successfully")
print("Press 'q' to quit (or Ctrl+C)")

try:
    while True:

        ret, frame = cap.read()

        if not ret:
            print("Error: could not read frame")
            break

        start_time = time.perf_counter()

        results = model.predict(
            source=frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRESHOLD,
            verbose=False
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = results[0]

        if result.boxes is not None and len(result.boxes) > 0:

            for box in result.boxes:

                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]

                label = (
                    f"{class_name} | "
                    f"conf={confidence*100:.1f}% | "
                    f"center=({cx},{cy}) | "
                    f"{elapsed_ms:.1f} ms"
                )

                # bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)

                # center
                cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)

                # label background
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.55
                thickness = 2

                text_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
                text_width, text_height = text_size

                text_x = x1
                text_y = max(y1 - 10, text_height + 10)

                cv2.rectangle(
                    frame,
                    (text_x, text_y - text_height - 8),
                    (text_x + text_width + 8, text_y + 4),
                    (0,255,0),
                    -1
                )

                cv2.putText(
                    frame,
                    label,
                    (text_x + 4, text_y),
                    font,
                    font_scale,
                    (0,0,0),
                    thickness,
                    cv2.LINE_AA
                )

        else:
            text = f"No traffic sign detected | {elapsed_ms:.1f} ms"

            cv2.putText(
                frame,
                text,
                (20,40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0,0,255),
                2,
                cv2.LINE_AA
            )

        cv2.imshow("YOLO Traffic Sign Detection", frame)

        # clean exit with q
        if cv2.waitKey(1) & 0xFF == ord("q"):
            print("Exit requested (q pressed)")
            break

except KeyboardInterrupt:
    print("\nExit requested (Ctrl+C pressed)")

finally:
    print("Releasing camera...")
    cap.release()
    cv2.destroyAllWindows()
    print("Camera released successfully")