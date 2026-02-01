FROM manelpuig/ros2-humble-limo-base:theconstruct

SHELL ["/bin/bash", "-c"]

# ------------------------------------------------------------
# Fix ROS2 apt source "Signed-By" conflicts in base image
# Keep ONE single ROS2 repo entry with ONE keyring.
# ------------------------------------------------------------
RUN set -eux; \
    apt-get update || true; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
    rm -rf /var/lib/apt/lists/*; \
    \
    # 1) Disable/remove any existing ROS2 source lists to avoid signed-by conflicts
    find /etc/apt/sources.list.d -maxdepth 1 -type f \
      \( -name "*ros2*.list" -o -name "*ros*.list" \) \
      -print -exec mv -f {} {}.disabled \; || true; \
    \
    # 2) Install ROS keyring (single source of truth)
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
      | gpg --dearmor -o /etc/apt/keyrings/ros-archive-keyring.gpg; \
    chmod 644 /etc/apt/keyrings/ros-archive-keyring.gpg; \
    \
    # 3) Add ONE ROS2 repo entry using that keyring
    . /etc/os-release; \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu ${UBUNTU_CODENAME} main" \
      > /etc/apt/sources.list.d/ros2.list; \
    \
    apt-get update; \
    rm -rf /var/lib/apt/lists/*

# -----------------------------
# 1) Base deps (stable)
# -----------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
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
      # USB / video utils
      libusb-1.0-0 \
      libusb-1.0-0-dev \
      udev \
      usbutils \
      v4l-utils \
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
      # Camera image transport plugins
      ros-humble-image-transport \
      ros-humble-image-transport-plugins \
      ros-humble-compressed-image-transport \
      \
      # What you explicitly want
      ros-humble-rviz2 \
      ros-humble-joint-state-publisher \
      ros-humble-tf-transformations \
      ros-humble-teleop-twist-keyboard \
      ros-humble-rmw-cyclonedds-cpp \
      ros-humble-rosbridge-server \
      \
      # Debugging
      net-tools \
    ; \
    rm -rf /var/lib/apt/lists/*

# 2) GUI tools (fast to change)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-humble-rqt \
    ros-humble-rqt-image-view \
    ros-humble-rqt-common-plugins \
&& rm -rf /var/lib/apt/lists/*

# -----------------------------
# Environment setup (.bashrc)
# -----------------------------
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /root/agilex_ws/install/setup.bash" >> /root/.bashrc && \
    echo "cd /root/agilex_ws" >> /root/.bashrc

CMD ["/bin/bash"]
