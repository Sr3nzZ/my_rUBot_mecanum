import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    rf2o_dir = get_package_share_directory("rf2o_laser_odometry")
    ydlidar_ros_dir = get_package_share_directory("ydlidar_ros2_driver")
    limo_base_dir = get_package_share_directory("limo_base")
    limo_bringup_dir = get_package_share_directory("limo_bringup")
    limo_gazebo = get_package_share_directory("limo_car")
    orbbec_camera_dir = get_package_share_directory("orbbec_camera")

    pub_tf = Node(
        package="limo_base",
        executable="tf_pub",
        output="screen",
        name="tf_pub_node",
    )
    base_link_to_laser_tf_node = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="base_link_to_base_laser_ydlidar",
        arguments=["0", "0", "0.18", "0", "0", "0", "1", "base_link", "laser_link"],
    )

    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [limo_base_dir, "/launch", "/limo_base.launch.py"]
                ),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [rf2o_dir, "/launch", "/rf2o_laser_odometry.launch.py"]
                ),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [ydlidar_ros_dir, "/launch", "/ydlidar.launch.py"]
                ),
            ),
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    [orbbec_camera_dir, "/launch", "/dabai.launch.py"]
                ),
                launch_arguments={
                'color_width': '640',
                'color_height': '480',
                'color_fps': '30', 
                'depth_width': '640',
                'depth_height': '400',
                'depth_fps': '30',
                'ir_width': '640',
                'ir_height': '400',
                'ir_fps': '30'
                }.items(),
            ),
            
            base_link_to_laser_tf_node,
        ]
    )
    