"""
This module contains a node that reads messages from a Limo's
depth camera and publish an image with all the predictions and a message
with the objects, their positions and depth.
"""

# YOLO service imports
import os
import rclpy
from my_robot_depth_navigation.services.images_service import *
from ultralytics import YOLO

from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy

from cv2 import IMREAD_UNCHANGED

# ROS2 core imports
from rclpy.node import Node
from rclpy.logging import get_logger

# ROS2 image processing imports
from sensor_msgs.msg import Image, CompressedImage

# Custom message import
from custom_msgs.msg import InferenceData

from pathlib import Path
from ament_index_python.packages import get_package_share_directory


YOLO_PREDICTIONS_TOPIC = "/yolo/predictions"

qos = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    history=HistoryPolicy.KEEP_LAST,
    depth=1
)

class YoloPredictionNode(Node):

    def __init__(self) -> None:
        """
        This node is responsible for reading the image messages from the depth camera
        publish the an image with the predictions, and a message with their x, y-coordinates.

        Parameters:
        ----------
        model_path : str
            The path to the YOLO model to be used for predictions.
        """

         # Sets node's name
        super().__init__("yolo_prediction_node")

        # ---------------------------------- Model Setup ------------------------------------

        self.declare_parameter('model', 'yolov8n_custom.pt')
        package_path = Path(get_package_share_directory('my_robot_ai_identification'))
        model = self.get_parameter('model').get_parameter_value().string_value
        model_file = package_path / 'models' / model

        if not os.path.exists(model_file):
            self.get_logger().error(f"YOLO model not found: {model_file}")
            raise FileNotFoundError(model_file)

        self.yolo = YOLO(model_file)

        # ---------------------------------- Camera Setup -----------------------------------

        self.declare_parameter('camera_topic', '/limo/camera')
        camera_topic = self.get_parameter('camera_topic').get_parameter_value().string_value

        self.create_subscription(
            CompressedImage,
            camera_topic + '/color/image_raw/compressed',
            self.color_image_callback,
            qos
        )

        self.create_subscription(
            Image,
            camera_topic + '/depth/image_raw',
            self.depth_image_callback,
            qos
        )

        # ---------------------------------- Publishers Setup -------------------------------

        self.prediction_publisher = self.create_publisher(
            Image,
            f'{YOLO_PREDICTIONS_TOPIC}/predictions_image',
            10
        )


        self.coordinates_publisher = self.create_publisher(
            InferenceData,
            f'{YOLO_PREDICTIONS_TOPIC}/predictions_data',
            10
        )

        # Computation variables
        self.color_image = None
        self.depth_image = None

        # Main loop
        self.create_timer(0.1, self.run)  # Run at 10 Hz


    def color_image_callback(self, msg: CompressedImage) -> None:
        """
        Callback for the raw image topic. It just saves the image to avoid
        interruption blocks.

        Parameters:
        ----------
        msg : Image
            The raw image message from the topic.
        """
        self.color_image = msg

    def depth_image_callback(self, msg: Image) -> None:
        """
        Callback for the depth image topic. It just saves the image to avoid
        interruption blocks.

        Parameters:
        ----------
        msg : Image
            The depth image message from the topic.
        """

        self.depth_image = msg


    def run(self) -> None:
        """
        Main loop responsible for performing the predictions.
        """

        # Early return if no images are read
        if self.color_image is None or self.depth_image is None:
            return
        
        color_image = self.color_image
        depth_image = self.depth_image

        # Avoids condition races
        self.color_image = None
        self.depth_image = None

        color_image = compressed_to_cv(color_image)
        depth_image = ros_to_cv(depth_image, encoding='32FC1')

        # Invalidate frame if one of the images is not valid
        if color_image is None or depth_image is None:
            return

        # Get predictions
        predictions = self.get_predictions(color_image)

        # Early return if no results
        if not predictions or len(predictions[0].boxes) == 0:
            return

        # If predictions publish the image and their coordinates
        self.publish_detections(color_image.copy(), depth_image.copy(), predictions[0]) # Just one prediction is performed as we send just one image at a time


    def get_predictions(self, img: Image) -> list:
        """
        Returns the predictions made by the YOLO model.

        Parameters:
        ----------
        img : Image
            The image to be predicted.

        Returns:
        -------
        list
            The predictions made by the YOLO model.
        """
        return self.yolo(img)

    
    def publish_detections(self, color_image: np.ndarray, depth_image: np.ndarray, prediction: list) -> None:

        # We assume one detection per image
        signal_prediction = prediction.boxes[0]
        signal_xyxy = signal_prediction.xyxy[0].to('cpu').detach().numpy().copy()
        centroid = ((signal_xyxy[2] - signal_xyxy[0]) / 2, (signal_xyxy[3] - signal_xyxy[1]) / 2)

        inference_data = InferenceData()
        inference_data.class_name = self.yolo.names[int(signal_prediction.cls)]

        confidence = float(signal_prediction.conf) * 100  # Confidence in percentage
        label = f"{inference_data.class_name}: {confidence:.2f}%"

        cv2.putText(color_image, label, (int(signal_xyxy[0]), int(signal_xyxy[1]) - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Print the bounding box and centroid
        cv2.rectangle(color_image, (int(signal_xyxy[0]), int(signal_xyxy[1])), (int(signal_xyxy[2]), int(signal_xyxy[3])), (0, 255, 0), 2)
        cv2.circle(color_image, (int(signal_xyxy[0]) + int(centroid[0]), int(signal_xyxy[1]) + int(centroid[1])), 5, (0, 255, 0), -1)

        depth_value = float(depth_image[int(signal_xyxy[1]) + int(centroid[1]), int(signal_xyxy[0]) +int(centroid[0])])
        inference_data.depth = depth_value

        # Draw the bounding box
        prediction_image = cv_to_ros(color_image)
        self.prediction_publisher.publish(prediction_image)
        self.coordinates_publisher.publish(inference_data)


def main() -> None:
    # Initialize ROS2
    rclpy.init()

    # Create YOLO service and node
    node = YoloPredictionNode()

    # Spin the node
    rclpy.spin(node)

    # Shutdown ROS2 when done
    node.destroy_node()
    rclpy.shutdown()