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
photos/
├── Stop/
├── Right/
├── Left/
├── Give/
├── Nothing/
└── Forbidden/
````
- Now you have to make photos (around 200) for each traffic sign with different positions, ilumination, environment, etc
    - open terminal in `/photos/Stop` folder, for exemple
    - run:  py -3.11 ..\1_capture_images.py
- First step is to resize to a 640x640 file format in a new structure, with the code `2_prepare_dataset.py`:
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
- Train a classification model with `3_generate_model.py`
- the model will be generated in: `runs/classify/train/weights/best.pt`
- To test the model prediction:
    - With the classification model `best.pt`:
        - Place `best.pt` in folder: /src/AI_projects/my_robot_ai_identification/models 
        - Open a terminal in main project folder
        - Verify on `4_classify_camera.py` python code MODEL_PATH = "/src/AI_projects/my_robot_ai_identification/models/best.pt":
