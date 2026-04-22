#!/bin/bash
set -e

source "/opt/ros/$ROS_DISTRO/setup.bash"
source "/root/orbbec_ws/install/setup.bash"
source "/root/ROS2_rUBot_mecanum_ws/install/setup.bash"

cd /root/ROS2_rUBot_mecanum_ws

export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

echo "Executing the main command..."
exec "$@"