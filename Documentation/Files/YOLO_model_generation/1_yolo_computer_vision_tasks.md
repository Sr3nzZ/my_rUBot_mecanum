# Computer Vision Tasks for Mobile Robotics Using YOLO

## Overview

In robot perception pipelines, four common vision tasks are typically
used:

-   Image Classification
-   Object Detection
-   Image Segmentation
-   Pose Estimation

These tasks progressively increase spatial understanding of the scene.

------------------------------------------------------------------------

## 1. Image Classification

Image classification assigns **one label per image**.

Example:

Input image → `STOP sign`

Used when only the object type matters, not its position.

Typical robotics use: - traffic sign recognition - object category
filtering - simple scene understanding

In our traffic‑sign project we use **classification**, because each
frame contains a single relevant sign.



------------------------------------------------------------------------

## 2. Object Detection

Object detection identifies:

-   object class
-   object position
-   bounding box coordinates

Example:

`STOP sign → (x, y, w, h)`

Useful when multiple objects appear simultaneously.

Typical robotics use:

-   obstacle detection
-   people detection
-   multi‑sign navigation


Detection could be added later to our project using datasets annotated
with tools such as **Roboflow**.

------------------------------------------------------------------------

## 3. Image Segmentation

Segmentation assigns a **class label to each pixel** in the image.

Instead of bounding boxes, it produces masks.

Typical robotics use:

-   road detection
-   hand contour extraction
-   grasp planning
-   environment mapping


Segmentation provides higher spatial precision but requires more
computation.

------------------------------------------------------------------------

## 4. Pose Estimation

Pose estimation detects **keypoints of articulated bodies**, typically
humans.

Example:

-   shoulders
-   elbows
-   wrists
-   knees

Typical robotics use:

-   gesture recognition
-   human‑robot interaction
-   hand tracking
-   collaborative robotics


Pose estimation is useful for interaction tasks such as detecting a
handshake or a raised hand.

![](../Images/07_Yolo/01_Yolo.png)

------------------------------------------------------------------------

## Why We Use YOLO

We use **YOLO (You Only Look Once)** because:

-   it runs in real time
-   it works well on CPU systems
-   it supports classification, detection, segmentation and pose
    estimation
-   it integrates easily with ROS 2 pipelines

Alternative frameworks exist:

-   Detectron2
-   Faster R‑CNN
-   EfficientDet
-   RT‑DETR

However, YOLO provides the best balance between speed, simplicity, and
accuracy for robotics education.

------------------------------------------------------------------------

## Why We Use the Ultralytics Library

We implement YOLO through the **Ultralytics Python library** because it:

-   simplifies training workflows
-   supports custom datasets
-   exports `.pt` models easily
-   runs efficiently on embedded platforms
-   integrates well with real‑time camera pipelines

Installation:

``` bash
pip install ultralytics
```

------------------------------------------------------------------------

## Current Strategy in the Traffic Sign Project

Current approach:

Traffic signs → **classification model**

Advantages:

-   simple dataset structure
-   fast training
-   efficient inference on mobile robots

Future extension:

Traffic signs → **object detection model**

This can be implemented by labeling bounding boxes using **Roboflow**
and retraining YOLO in detection mode.

This upgrade allows the robot to detect multiple signs simultaneously
inside the same image.
