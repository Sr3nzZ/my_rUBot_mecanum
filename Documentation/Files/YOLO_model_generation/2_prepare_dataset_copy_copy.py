from pathlib import Path
import shutil
import random
import cv2
import numpy as np
from PIL import Image

# ============================================================
# Configuration
# ============================================================
RAW_DATASET_DIR = Path("photos_g2")
OUTPUT_DATASET_DIR = Path("traffic_sign_dataset_g2_2")

CLASSES = [
    "Stop",
    "Right",
    "Left",
    "Give",
    "Nothing",
    "Forbidden",
]

TRAIN_RATIO = 0.80
IMG_SIZE = 640

VALID_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".webp"]

random.seed(42)


def extract_signal_circle(src_path: Path, dst_path: Path, size: int = 640):

    img = cv2.imread(str(src_path))
    if img is None:
        print(f"Error loading {src_path}")
        return

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (7, 7), 0)

    # 🔥 1. edges més suaus (millor per senyals reals)
    edges = cv2.Canny(gray, 30, 120)

    # 🔥 2. tancar forats (MOLT important)
    kernel = np.ones((5, 5), np.uint8)
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    best_cnt = None
    best_score = 0

    for cnt in contours:

        area = cv2.contourArea(cnt)
        if area < 1000:
            continue

        perimeter = cv2.arcLength(cnt, True)
        if perimeter == 0:
            continue

        circularity = 4 * np.pi * (area / (perimeter * perimeter))

        # bounding box check (evita formes estranyes)
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)

        # cercle real:
        # - circularity alta
        # - aspect ratio ~1
        if circularity > 0.65 and 0.7 < aspect_ratio < 1.3:

            if circularity > best_score:
                best_score = circularity
                best_cnt = cnt

    # fallback segur
    if best_cnt is None:
        print(f"No circle detected in {src_path}")
        resized = cv2.resize(img, (size, size))
        cv2.imwrite(str(dst_path), resized)
        return

    (x, y), radius = cv2.minEnclosingCircle(best_cnt)
    x, y, radius = int(x), int(y), int(radius)

    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (x, y), radius, 255, -1)

    result = cv2.bitwise_and(img, img, mask=mask)

    x1 = max(x - radius, 0)
    y1 = max(y - radius, 0)
    x2 = min(x + radius, img.shape[1])
    y2 = min(y + radius, img.shape[0])

    cropped = result[y1:y2, x1:x2]

    final = cv2.resize(cropped, (size, size))

    cv2.imwrite(str(dst_path), final)

def prepare_folders():
    """
    Create train/val folder structure.
    """
    for split in ["train", "val"]:
        for class_name in CLASSES:
            folder = OUTPUT_DATASET_DIR / split / class_name
            folder.mkdir(parents=True, exist_ok=True)


def process_class(class_name: str):
    """
    Split images of one class into train and val.
    """
    input_class_dir = RAW_DATASET_DIR / class_name

    if not input_class_dir.exists():
        print(f"WARNING: Folder not found: {input_class_dir}")
        return

    image_paths = [
        p for p in input_class_dir.iterdir()
        if p.suffix.lower() in VALID_EXTENSIONS
    ]

    random.shuffle(image_paths)

    n_total = len(image_paths)
    n_train = int(n_total * TRAIN_RATIO)

    train_images = image_paths[:n_train]
    val_images = image_paths[n_train:]

    print(f"{class_name}: {n_total} images -> {len(train_images)} train, {len(val_images)} val")

    for split, images in [("train", train_images), ("val", val_images)]:
        for i, src_path in enumerate(images):
            dst_filename = f"{class_name.lower()}_{i:04d}.jpg"
            dst_path = OUTPUT_DATASET_DIR / split / class_name / dst_filename
            extract_signal_circle(src_path, dst_path, IMG_SIZE)


def main():
    if OUTPUT_DATASET_DIR.exists():
        print(f"Removing existing folder: {OUTPUT_DATASET_DIR}")
        shutil.rmtree(OUTPUT_DATASET_DIR)

    prepare_folders()

    for class_name in CLASSES:
        process_class(class_name)

    print("\nDataset prepared successfully.")
    print(f"Output folder: {OUTPUT_DATASET_DIR}")


if __name__ == "__main__":
    main()