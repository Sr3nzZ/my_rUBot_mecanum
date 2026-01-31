#!/bin/bash
set -e

# setup ros2 environment
source "/opt/ros/$ROS_DISTRO/setup.bash"

# source additional workspace setup
if [ -f "/root/agilex_ws/install/setup.bash" ]; then
    source "/root/agilex_ws/install/setup.bash"
fi

exec "$@"
