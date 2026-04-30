import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # ================================================================
    # Launch configurations
    # ================================================================
    robot_model = LaunchConfiguration('robot_model')

    mecanum_serial_port = LaunchConfiguration('mecanum_serial_port')
    rplidar_serial_port = LaunchConfiguration('rplidar_serial_port')
    rplidar_frame_id = LaunchConfiguration('rplidar_frame_id')

    color_width = LaunchConfiguration('color_width')
    color_height = LaunchConfiguration('color_height')
    color_fps = LaunchConfiguration('color_fps')
    color_format = LaunchConfiguration('color_format')

    depth_width = LaunchConfiguration('depth_width')
    depth_height = LaunchConfiguration('depth_height')
    depth_fps = LaunchConfiguration('depth_fps')
    depth_registration = LaunchConfiguration('depth_registration')

    enable_ir = LaunchConfiguration('enable_ir')
    enable_point_cloud = LaunchConfiguration('enable_point_cloud')
    enable_accel = LaunchConfiguration('enable_accel')
    enable_gyro = LaunchConfiguration('enable_gyro')
    connection_delay = LaunchConfiguration('connection_delay')

    # ================================================================
    # Declare arguments
    # ================================================================
    declare_robot_model = DeclareLaunchArgument(
        'robot_model',
        default_value='robot_arm/my_simple_robot.urdf',
        description='URDF/XACRO path inside my_robot_description/urdf'
    )

    declare_mecanum_serial_port = DeclareLaunchArgument(
        'mecanum_serial_port',
        default_value='/dev/ttyACM0',
        description='Serial port for Nano mecanum driver'
    )

    declare_rplidar_serial_port = DeclareLaunchArgument(
        'rplidar_serial_port',
        default_value='/dev/ttyUSB0',
        description='Serial port for RPLidar'
    )

    declare_rplidar_frame_id = DeclareLaunchArgument(
        'rplidar_frame_id',
        default_value='base_link',
        description='Frame ID for RPLidar data'
    )

    # Gemini2 parameters: same as the terminal command that works
    declare_color_width = DeclareLaunchArgument(
        'color_width',
        default_value='640',
        description='Gemini2 RGB image width'
    )

    declare_color_height = DeclareLaunchArgument(
        'color_height',
        default_value='480',
        description='Gemini2 RGB image height'
    )

    declare_color_fps = DeclareLaunchArgument(
        'color_fps',
        default_value='15',
        description='Gemini2 RGB FPS'
    )

    declare_color_format = DeclareLaunchArgument(
        'color_format',
        default_value='MJPG',
        description='Gemini2 RGB format'
    )

    declare_depth_width = DeclareLaunchArgument(
        'depth_width',
        default_value='640',
        description='Gemini2 depth image width'
    )

    declare_depth_height = DeclareLaunchArgument(
        'depth_height',
        default_value='400',
        description='Gemini2 depth image height'
    )

    declare_depth_fps = DeclareLaunchArgument(
        'depth_fps',
        default_value='15',
        description='Gemini2 depth FPS'
    )

    declare_depth_registration = DeclareLaunchArgument(
        'depth_registration',
        default_value='false',
        description='Align depth image to color image'
    )

    declare_enable_ir = DeclareLaunchArgument(
        'enable_ir',
        default_value='false',
        description='Enable IR stream'
    )

    declare_enable_point_cloud = DeclareLaunchArgument(
        'enable_point_cloud',
        default_value='false',
        description='Enable point cloud generation'
    )

    declare_enable_accel = DeclareLaunchArgument(
        'enable_accel',
        default_value='false',
        description='Enable accelerometer'
    )

    declare_enable_gyro = DeclareLaunchArgument(
        'enable_gyro',
        default_value='false',
        description='Enable gyroscope'
    )

    declare_connection_delay = DeclareLaunchArgument(
        'connection_delay',
        default_value='3000',
        description='Gemini2 connection delay in milliseconds'
    )

    # ================================================================
    # Robot description + robot_state_publisher
    # ================================================================
    robot_description_content = Command([
        'xacro ',
        PathJoinSubstitution([
            FindPackageShare('my_robot_description'),
            'urdf',
            robot_model
        ])
    ])

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            {'robot_description': robot_description_content},
        ]
    )

    # ================================================================
    # Mecanum robot driver
    # ================================================================
    robot_driver_hw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('my_robot_bringup'),
                'launch',
                'robot_driver_hw.launch.py'
            )
        ),
        launch_arguments={
            'mecanum_serial_port': mecanum_serial_port,
        }.items()
    )

    # ================================================================
    # Orbbec Gemini2 camera
    #
    # IMPORTANT:
    # Only pass the parameters that were verified to work from terminal.
    # Do not force extra internal parameters unless needed.
    # ================================================================
    gemini2_hw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('orbbec_camera'),
                'launch',
                'gemini2.launch.py'
            )
        ),
        launch_arguments={
            'color_width': color_width,
            'color_height': color_height,
            'color_fps': color_fps,
            'color_format': color_format,

            'depth_width': depth_width,
            'depth_height': depth_height,
            'depth_fps': depth_fps,
            'depth_registration': depth_registration,

            'enable_ir': enable_ir,
            'enable_point_cloud': enable_point_cloud,
            'enable_accel': enable_accel,
            'enable_gyro': enable_gyro,

            'connection_delay': connection_delay,
        }.items()
    )

    # ================================================================
    # RPLidar
    # ================================================================
    rplidar_hw_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('my_robot_bringup'),
                'launch',
                'rplidar_hw.launch.py'
            )
        ),
        launch_arguments={
            'rplidar_serial_port': rplidar_serial_port,
            'rplidar_frame_id': rplidar_frame_id,
        }.items()
    )

    # ================================================================
    # Build launch description
    # ================================================================
    ld = LaunchDescription()

    ld.add_action(declare_robot_model)
    ld.add_action(declare_mecanum_serial_port)
    ld.add_action(declare_rplidar_serial_port)
    ld.add_action(declare_rplidar_frame_id)

    ld.add_action(declare_color_width)
    ld.add_action(declare_color_height)
    ld.add_action(declare_color_fps)
    ld.add_action(declare_color_format)

    ld.add_action(declare_depth_width)
    ld.add_action(declare_depth_height)
    ld.add_action(declare_depth_fps)
    ld.add_action(declare_depth_registration)

    ld.add_action(declare_enable_ir)
    ld.add_action(declare_enable_point_cloud)
    ld.add_action(declare_enable_accel)
    ld.add_action(declare_enable_gyro)
    ld.add_action(declare_connection_delay)

    # Start robot_state_publisher first
    ld.add_action(robot_state_publisher_node)

    # Start Gemini2 first, with no USB serial devices active yet
    ld.add_action(gemini2_hw_launch)

    # Start Arduino / mecanum driver after Gemini2 initialization
    ld.add_action(
        TimerAction(
            period=10.0,
            actions=[robot_driver_hw_launch]
        )
    )

    # Start RPLidar last
    ld.add_action(
        TimerAction(
            period=15.0,
            actions=[rplidar_hw_launch]
        )
    )

    return ld