# ===================================================================
# Jetson Nano (ARM64) - ROS2 Humble + Workspaces:
# - my_rUBot_mecanum (your repo)
# - OrbbecSDK_ROS2 (inside same ws/src)
# + OrbbecViewer SDK extracted to /root/orbbec_sdk
# ===================================================================

FROM theconstructai/limo:humble-v3

SHELL ["/bin/bash", "-c"]

# --- Fix expired ROS apt key in base image (Open Robotics) ---
RUN set -eux; \
    # Temporarily disable ROS repo to allow apt update
    if [ -f /etc/apt/sources.list.d/ros2.list ]; then \
      mv /etc/apt/sources.list.d/ros2.list /etc/apt/sources.list.d/ros2.list.disabled; \
    fi; \
    if [ -f /etc/apt/sources.list.d/ros2-latest.list ]; then \
      mv /etc/apt/sources.list.d/ros2-latest.list /etc/apt/sources.list.d/ros2-latest.list.disabled; \
    fi; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
    rm -rf /var/lib/apt/lists/*; \
    \
    # Install new ROS keyring
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      | gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg; \
    \
    # Re-create ROS2 repo entry using signed-by keyring
    . /etc/os-release; \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu ${UBUNTU_CODENAME} main" \
      > /etc/apt/sources.list.d/ros2.list; \
    \
    # Now update with ROS repo enabled
    apt-get update; \
    rm -rf /var/lib/apt/lists/*


# -----------------------------
# 1) System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    # X11 graphical support (for OrbbecViewer)
    x11-apps \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libglu1-mesa \
    mesa-utils \
    libqt5x11extras5 \
    libxkbcommon-x11-0 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libxtst6 \
    \
    # USB deps
    libusb-1.0-0 \
    libusb-1.0-0-dev \
    udev \
    usbutils \
    \
    # Dev tools
    build-essential \
    cmake \
    python3-colcon-common-extensions \
    python3-pip \
    python3-rosdep \
    unzip \
    git \
    iputils-ping \
    python3-serial \
    \
    # Camera 3D plugins
    ros-humble-image-transport \
    ros-humble-image-transport-plugins \
    ros-humble-compressed-image-transport \
    \
    # ROS 2 add-ons (keep if you really need them)
    ros-humble-rviz2 \
    ros-humble-joint-state-publisher \
    ros-humble-tf-transformations \
    ros-humble-teleop-twist-keyboard \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rosbridge-server \
    && rm -rf /var/lib/apt/lists/*

# rosdep (safe if already initialized)
RUN rosdep init || true && rosdep update

# -----------------------------
# Environment setup (.bashrc)
# -----------------------------
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /root/agilex_ws/install/setup.bash" >> /root/.bashrc && \
    echo "cd agilex_ws" >> /root/.bashrc

CMD ["/bin/bash"]
