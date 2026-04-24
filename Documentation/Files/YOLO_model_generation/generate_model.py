from ultralytics import YOLO

def main():

    print("Loading model...")

    model = YOLO("yolo11n-cls.pt")

    print("Starting training...")

    model.train(
        data="traffic_sign_dataset",
        epochs=50,
        imgsz=640,
        batch=8,
        patience=10,
        optimizer="AdamW",
        lr0=0.001,
        device="cpu"
    )

    print("Training finished.")

if __name__ == "__main__":
    main()