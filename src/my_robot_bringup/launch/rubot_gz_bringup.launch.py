import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    pkg_bringup = get_package_share_directory("my_robot_bringup")

    world = LaunchConfiguration("world")
    model_sdf = LaunchConfiguration("model_sdf")
    bridge_yaml = LaunchConfiguration("bridge_yaml")

    default_world = os.path.join(pkg_bringup, "worlds", "empty_gz.world.sdf")
    default_model = os.path.join(pkg_bringup, "models", "rubot_mecanum", "model.sdf")
    default_bridge = os.path.join(pkg_bringup, "config", "ros_gz_bridge_camera.yaml")

    # 1) Start Gazebo Sim
    gz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory("ros_gz_sim"), "launch", "gz_sim.launch.py")
        ),
        launch_arguments={"gz_args": ["-r ", world]}.items(),
    )

    # 2) Spawn robot
    spawn = Node(
        package="ros_gz_sim",
        executable="create",
        output="screen",
        arguments=[
            "-name", "rubot_mecanum",
            "-file", model_sdf,
            "-x", "0", "-y", "0", "-z", "0.05",
        ],
    )

    # 3) Bridge via config_file
    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        parameters=[
            {"use_sim_time": True},
            {"config_file": bridge_yaml},
        ],
    )

    delayed = TimerAction(period=2.0, actions=[spawn, bridge])

    return LaunchDescription([
        DeclareLaunchArgument("world", default_value=default_world),
        DeclareLaunchArgument("model_sdf", default_value=default_model),
        DeclareLaunchArgument("bridge_yaml", default_value=default_bridge),

        gz_launch,
        delayed,
    ])
