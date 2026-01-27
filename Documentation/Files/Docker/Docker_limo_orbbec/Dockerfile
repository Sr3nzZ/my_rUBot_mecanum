# ===================================================================
# Jetson Nano (ARM64) - ROS2 Humble + Workspaces:
# - my_rUBot_mecanum (your repo)
# - OrbbecSDK_ROS2 (inside same ws/src)
# + OrbbecViewer SDK extracted to /root/orbbec_sdk
# ===================================================================

FROM theconstructai/limo:humble-v3

SHELL ["/bin/bash", "-c"]

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
    # ROS 2 add-ons (keep if you really need them)
    ros-humble-rviz2 \
    ros-humble-joint-state-publisher \
    ros-humble-joint-state-publisher-gui \
    ros-humble-gazebo-plugins \
    ros-humble-nav2-bringup \
    ros-humble-nav2-simple-commander \
    ros-humble-tf-transformations \
    ros-humble-cartographer-ros \
    ros-humble-teleop-twist-keyboard \
    ros-humble-rmw-cyclonedds-cpp \
    ros-humble-rosbridge-server \
    && rm -rf /var/lib/apt/lists/*

# rosdep (safe if already initialized)
RUN rosdep init || true && rosdep update

# -----------------------------
# 2) Your workspace + Orbbec ROS2 wrapper
# -----------------------------
WORKDIR /root
RUN git clone https://github.com/manelpuig/my_rUBot_mecanum.git

# Clone Orbbec wrapper into the same ws
WORKDIR /root/my_rUBot_mecanum/src
RUN git clone --branch main https://github.com/orbbec/OrbbecSDK_ROS2.git

# Install deps + build once
WORKDIR /root/my_rUBot_mecanum
RUN source /opt/ros/humble/setup.bash && \
    rosdep install --from-paths src --ignore-src -r -y && \
    colcon build

# -----------------------------
# 3) OrbbecViewer SDK (zip -> /root/orbbec_sdk)
# -----------------------------
ARG ORBBEC_VIEWER_ZIP=OrbbecViewer_v1.10.27_202509260950_arm64_release.zip

WORKDIR /root
RUN mkdir -p /root/orbbec_sdk

# Copy zip file into image, extract, then remove zip to save space
COPY ${ORBBEC_VIEWER_ZIP} /tmp/orbbec_viewer.zip

RUN unzip -q /tmp/orbbec_viewer.zip -d /tmp/orbbec_unzipped && \
    # Copy the *contents* of the extracted folder into /root/orbbec_sdk
    # (handles cases where zip contains a top-level directory)
    if [ -d "/tmp/orbbec_unzipped/OrbbecViewer_v1.10.27_202509260950_arm64_release" ]; then \
      cp -r /tmp/orbbec_unzipped/OrbbecViewer_v1.10.27_202509260950_arm64_release/* /root/orbbec_sdk/ ; \
    else \
      cp -r /tmp/orbbec_unzipped/* /root/orbbec_sdk/ ; \
    fi && \
    rm -rf /tmp/orbbec_unzipped /tmp/orbbec_viewer.zip

# Do NOT install udev rules here: do it on the Jetson host.
# Just ensure script is executable (if present).
RUN if [ -f "/root/orbbec_sdk/script/install_udev_rules.sh" ]; then \
      chmod +x /root/orbbec_sdk/script/install_udev_rules.sh ; \
    fi

# -----------------------------
# 4) Environment setup (.bashrc)
# -----------------------------
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /root/my_rUBot_mecanum/install/setup.bash" >> /root/.bashrc && \
    echo "export ORBBEC_SDK_HOME=/root/orbbec_sdk" >> /root/.bashrc

CMD ["/bin/bash"]
