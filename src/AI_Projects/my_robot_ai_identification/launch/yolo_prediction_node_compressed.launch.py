from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        # -----------------------
        # Republish color camera -> compressed
        # -----------------------
        Node(
            package='image_transport',
            executable='republish',
            name='republish_color',
            output='screen',
            arguments=[
                'raw', 'compressed',
                '/limo/camera/image_raw',
            ]
        ),

        # -----------------------
        # Republish depth camera -> compressed
        # -----------------------
        Node(
            package='image_transport',
            executable='republish',
            name='republish_depth',
            output='screen',
            arguments=[
                'raw', 'compressed',
                '/limo/camera/depth/image_raw'
            ]
        ),

        # -----------------------
        # Nodo YOLO que procesa imágenes comprimidas
        # -----------------------
        Node(
            package='my_robot_depth_navigation',
            executable='yolo_prediction_node_compressed',
            name='yolo_prediction_node',
            output='screen',
            parameters=[{
                'model': 'yolov8n_custom.pt',
                'camera_topic': '/camera'
            }]
        )
    ])