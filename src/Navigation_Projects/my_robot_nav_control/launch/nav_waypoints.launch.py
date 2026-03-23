#!/usr/bin/env python3
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_nav_control')

    default_wp_file = os.path.join(pkg_share, 'config', 'waypoints_sw.yaml')

    wp_file_arg = DeclareLaunchArgument(
        'wp_file',
        default_value=default_wp_file,
        description='Path to external waypoint YAML file'
    )

    nav_waypoints_node = Node(
        package='my_robot_nav_control',
        executable='nav_waypoints_exec',
        name='nav_waypoints_node',
        output='screen',
        parameters=[
            {'wp_file': LaunchConfiguration('wp_file')}
        ]
    )

    return LaunchDescription([
        wp_file_arg,
        nav_waypoints_node
    ])