from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node

def generate_launch_description():
    image_width = LaunchConfiguration('image_width')
    image_height = LaunchConfiguration('image_height')
    video_device = LaunchConfiguration('video_device')

    declare_width = DeclareLaunchArgument(
        'image_width',
        default_value='640',
        description='Width of the camera image'
    )
    declare_height = DeclareLaunchArgument(
        'image_height',
        default_value='480',
        description='Height of the camera image'
    )
    declare_device = DeclareLaunchArgument(
        'video_device',
        default_value='/dev/video0',
        description='Video device for USB camera'
    )

    usb_cam_node = Node(
        package='v4l2_camera',
        executable='v4l2_camera_node',
        name='camera',
        output='screen',
        respawn=True,
        respawn_delay=2.0,
        parameters=[{
            'video_device': video_device,
            'image_size': [640, 480],
            # opcional:
            # 'frame_rate': 30.0,
            # 'camera_frame_id': 'camera_link',
        }]
    )

    return LaunchDescription([
        declare_width,
        declare_height,
        declare_device,
        usb_cam_node
    ])
