from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # -----------------------
        # Nodo YOLO que procesa imágenes comprimidas
        # -----------------------
        Node(
            package='my_robot_depth_navigation',
            executable='yolo_prediction_node',
            name='yolo_prediction_node',
            output='screen',
            parameters=[{
                'model': 'yolov8n_custom.pt',
                'camera_topic': '/camera'
            }]
        )
    ])