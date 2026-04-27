#!/usr/bin/env python3

from ultralytics import YOLO
import cv2
import time
import sys
import os

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy


# ==============================
# GLOBAL PARAMETERS
# ==============================
MODEL_PATH = "models/yolov8n_custom.pt"

IMAGE_TOPIC = "/image_raw"

WINDOW_NAME = "YOLO Traffic Sign Detection"

CONF_THRESHOLD = 0.50
IMG_SIZE = 160

PROCESS_WIDTH = 160
PROCESS_HEIGHT = 120
DISPLAY_SCALE = 4

SHOW_WINDOW = True


# ==============================
# CHECK MODEL
# ==============================
if not os.path.exists(MODEL_PATH):
    print(f"Error: model not found: {MODEL_PATH}")
    sys.exit(1)


# ==============================
# LOAD MODEL
# ==============================
model = YOLO(MODEL_PATH)

print("Model loaded correctly")
print("Model classes:")
print(model.names)


class YoloImageRawNode(Node):

    def __init__(self):
        super().__init__("yolo_image_raw_node")

        self.bridge = CvBridge()

        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.subscription = self.create_subscription(
            Image,
            IMAGE_TOPIC,
            self.image_callback,
            qos
        )

        if SHOW_WINDOW:
            cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

        self.get_logger().info(f"Subscribed to {IMAGE_TOPIC}")
        self.get_logger().info("Press Ctrl+C to stop")

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(
                msg,
                desired_encoding="bgr8"
            )
        except Exception as e:
            self.get_logger().error(f"Error converting image: {e}")
            return

        process_frame = cv2.resize(
            frame,
            (PROCESS_WIDTH, PROCESS_HEIGHT)
        )

        start_time = time.perf_counter()

        results = model.predict(
            source=process_frame,
            imgsz=IMG_SIZE,
            conf=CONF_THRESHOLD,
            verbose=False
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        result = results[0]

        display_frame = cv2.resize(
            process_frame,
            (
                PROCESS_WIDTH * DISPLAY_SCALE,
                PROCESS_HEIGHT * DISPLAY_SCALE
            ),
            interpolation=cv2.INTER_NEAREST
        )

        detections = 0

        if result.boxes is not None and len(result.boxes) > 0:
            detections = len(result.boxes)

            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                # YOLO detects on process_frame.
                # display_frame is scaled, so box coordinates must also be scaled.
                x1 *= DISPLAY_SCALE
                y1 *= DISPLAY_SCALE
                x2 *= DISPLAY_SCALE
                y2 *= DISPLAY_SCALE

                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]

                cx = int((x1 + x2) / 2)
                cy = int((y1 + y2) / 2)

                label = (
                    f"{class_name} "
                    f"{confidence * 100:.1f}% "
                    f"center=({cx},{cy})"
                )

                cv2.rectangle(
                    display_frame,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    display_frame,
                    (cx, cy),
                    5,
                    (0, 0, 255),
                    -1
                )

                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.55
                thickness = 2

                text_size, _ = cv2.getTextSize(
                    label,
                    font,
                    font_scale,
                    thickness
                )

                text_width, text_height = text_size

                label_x = x1
                label_y = max(y1 - 10, text_height + 10)

                cv2.rectangle(
                    display_frame,
                    (label_x, label_y - text_height - 8),
                    (label_x + text_width + 8, label_y + 4),
                    (0, 255, 0),
                    -1
                )

                cv2.putText(
                    display_frame,
                    label,
                    (label_x + 4, label_y),
                    font,
                    font_scale,
                    (0, 0, 0),
                    thickness,
                    cv2.LINE_AA
                )

        info_text = (
            f"detections={detections} | "
            f"conf>{CONF_THRESHOLD:.2f} | "
            f"{elapsed_ms:.1f} ms"
        )

        cv2.rectangle(
            display_frame,
            (0, 0),
            (display_frame.shape[1], 35),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            display_frame,
            info_text,
            (15, 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        if SHOW_WINDOW:
            cv2.imshow(WINDOW_NAME, display_frame)
            cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)

    node = YoloImageRawNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nInterrupted by user Ctrl+C")
    finally:
        node.destroy_node()
        cv2.destroyAllWindows()
        cv2.waitKey(1)
        rclpy.shutdown()
        print("Node stopped correctly")


if __name__ == "__main__":
    main()