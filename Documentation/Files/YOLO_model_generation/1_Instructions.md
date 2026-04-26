# *YOLO Model generation*

You have to install:
- Ultralytics library and other needed libraries
````bash
py -3.11 -m pip install ultralytics
py -3.11 -m pip uninstall numpy
py -3.11 -m pip install "numpy<2.0"
py -3.11 -m pip install pillow
py -3.11 -m pip install opencv-python
````
- You need an initial structure:
````python
raw_dataset/
├── Stop/
├── Right/
├── Left/
├── Give/
├── Nothing/
└── Forbidden/
````
- First step is to resize to a 640x640 file format in a new structure, with the cose `prepare_dataset.py`:
````python
traffic_sign_dataset/
├── train/
│   ├── Stop/
│   ├── Right/
│   ├── Left/
│   ├── Give/
│   ├── Nothing/
│   └── Forbidden/
└── val/
    ├── Stop/
    ├── Right/
    ├── Left/
    ├── Give/
    ├── Nothing/
    └── Forbidden/
````
> See the value: TRAIN_RATIO = 0.80   # 80% train, 20% val
- Train a classification model with `generate_model.py`
- the model will be generated in: `runs/classify/train/weights/best.pt`
