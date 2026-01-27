# ROS 2 Humble – Lab Network Setup

## 1. Network topology and ROS 2 setup

This document describes the network setup of a teaching lab with a mobile robot and a control PC, both running ROS 2 Humble.

### 1.1 Physical network

- **WiFi router (mobile router / hotspot)**

  - Provides DHCP and fixed IP addresses in the `192.168.1.x` network.
- **Robot 1**

  - Hardware: Raspberry Pi 4
  - OS: Ubuntu Server 22.04
  - ROS: ROS 2 Humble
  - IP address (fixed): `192.168.1.14`
- **Control PC**

  - Hardware: PC with Ubuntu 22.04
  - ROS: ROS 2 Humble
  - IP address (fixed): `192.168.1.15`

Both machines are connected to the same WiFi router and are in the same Layer-2 network.

### 1.2 ROS 2 environment

The Ubuntu22.04 installations is performed, either with:
- PC Ubuntu22.04 with ROS2 Humble installed.
- External SSD USB Disc with Ubuntu 22.04 and ROS2 Humble installed.
- or Docker container (on PC Unix) with ROS2 Humble installed.

In each case the communicacion is ensured by a proper DDS (Data Distribution Service) configuration.

## 2. ROS Networking Middleware

ROS2 network communication is based on DDS (Data Distribution Service) that provides:

- Discovery: nodes find each other automatically.

- Transport: messages go over UDP (usually) on your LAN.

- QoS (Quality of Service): rules for reliability, history, durability, deadlines, etc.

- Multicast/Broadcast (often) for discovery, then unicast for data.

So, DDS is basically the networking middleware that makes ROS 2 communication possible and is accessed through an abstraction layer called RMW (ROS Middleware Interface).

There are different RMW implementations:
- Fast DDS (Default in ROS2)

- Cyclone DDs


### 2.1. Fast DDS (rmw_fastrtps_cpp)

It was developped by eProsima (https://docs.ros.org/en/humble/Installation/RMW-Implementations/DDS-Implementations/Working-with-eProsima-Fast-DDS.html)

Typical strengths:

- Very widely used in ROS 2 ecosystem, lots of examples.

- Good performance and many features; integrates well with some ROS 2 stacks.

Typical weaknesses

- In “messy networks” (hotspots, Wi-Fi isolation, multiple interfaces), discovery can feel more fragile.

- Complex Configuration (profiles XML)

It can be selected with an environment variable:
````shell
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp     # Fast DDS (eProsima)
````

### 2.2. Cyclone DDS (rmw_cyclonedds_cpp)

It was developped by Eclipse (https://docs.ros.org/en/humble/Installation/RMW-Implementations/DDS-Implementations/Working-with-Eclipse-CycloneDDS.html)

Typical strengths

- Often more predictable discovery and behavior in “simple LAN” robotics setups.

- Strong reputation for robustness and good interoperability.

- Simple Configuration via CycloneDDS XML (CYCLONEDDS_URI) is straightforward for static peers / restricted discovery.

Typical weaknesses

- Some complex multi-network setups require careful interface selection.

It can be selected with an environment variable:
````shell
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp     # Fast DDS (eProsima)
````

## 3. Laboratory network configuration

To make the system robust and independent of multicast quirks and startup order, we explicitly choose and configure CycloneDDS to use unicast peer discovery between the PC and the robot.

With this configuration:

- Each machine (PC or rUBot) uses its own fixed IP address for DDS.

- Each machine is given the other machine as a peer (explicit unicast address).

- Multicast can still be allowed, but discovery no longer depends on it.

We will:

- Define `ROS_AUTOMATIC_DISCOVERY_RANGE` environment variable values: OFF, LOCALHOST, SUBNET
    - This variable controls how far ROS 2 tries to auto-discover peers.
        - SUBNET (default)

            - Discovers any node reachable via multicast on the local subnet.

            - Use when:

                - Normal home/lab router

                - Multicast works

                - You want “plug and play discovery”

        - LOCALHOST

            - Discovers only nodes on the same machine.

            - Use when:

                - You run everything locally (Gazebo + Nav2 + RViz on one PC)

                - You want to prevent accidental network chatter on a shared LAN

        - OFF

            - Disables automatic discovery completely (even local-machine discovery).

            - Use when:

                - You want only explicit discovery via ROS_STATIC_PEERS (and/or Cyclone <Peers>)

                - Hotspot/mobile router situations where multicast is broken

                - Multi-robot labs where you want strict control over who sees who

- Define `ROS_STATIC_PEERS` to specify robot/PC IP to communicate with
- maintain the `cyclonedds.xml` file for generic network configurations (NetworkInterface, etc)

- Update `.bashrc` to use these configs
    - On the PC: 

        ````bash
        # --- ROS 2 base ---
        source /opt/ros/humble/setup.bash
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash

        # --- Your workspace ---
        source /root/ROS2_rUBot_mecanum_ws/install/setup.bash
        cd ~/Desktop/ROS2_rUBot_mecanum_ws

        # --- Gazebo / RViz usability ---
        export GAZEBO_MODEL_PATH=/root/ROS2_rUBot_mecanum_ws/src/my_robot_bringup/models:${GAZEBO_MODEL_PATH}
        export QT_QPA_PLATFORM=xcb  # good default for RViz2 on many systems

        # --- ROS 2 networking ---
        export ROS_DOMAIN_ID=1
        export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp

        # Option A: normal discovery (if multicast works)
        # unset ROS_AUTOMATIC_DISCOVERY_RANGE
        # unset ROS_STATIC_PEERS

        # Option B: robust hotspot mode (recommended)
        export ROS_AUTOMATIC_DISCOVERY_RANGE=OFF
        export ROS_STATIC_PEERS="192.168.1.45"   # for multiple peers: "192.168.1.45;192.168.1.46"

        # CycloneDDS XML (interface binding, peers, etc.)
        export CYCLONEDDS_URI=file:///root/ROS2_rUBot_mecanum_ws/network_config/Humble2/config/cyclonedds.xml
        ````
    - On the robot:

        ````bash
        source /opt/ros/humble/setup.bash
        source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
        source /home/ubuntu/ROS2_rUBot_mecanum_ws/install/setup.bash
        cd /home/ubuntu/ROS2_rUBot_mecanum_ws
        export ROS_DOMAIN_ID=1
        export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
        export ROS_AUTOMATIC_DISCOVERY_RANGE=OFF
        export ROS_STATIC_PEERS="192.168.1.55"   # PC IP
        export CYCLONEDDS_URI=file:///home/ubuntu/cyclonedds.xml
        ````

## 3. ROS2 environment on Linux DualBoot PC based on Docker containers

Computers with DualBoot (Windows-Linux) we need to use a Docker based setup to run ROS2 Humble.

A proper Docker Image has been created with the custom configuration on Dockerfile and uploaded to my DockerHub account (https://hub.docker.com/r/manelpuig/ros2-humble-biorobub-pc).

**Students** in the lab they only need to:
- Unzip the `ros2-humble-biorobub.zip` file in a `~/Desktop/rob` folder on Linux PC
- review on:
    - `docker-compose.yml` file: `ROS_DOMAIN_ID` variable to match your robot.
    - `cyclonedds_pc.xml` file: IPs to match your PC and robot.
    - `cyclonedds_robot.xml` file: IPs to match your robot and PC.
- Open a terminal in the `~/Desktop/rob/ros2-humble-biorobub` folder and run:
    ````bash
    xhost +local:root            # allow X11 for graphs in container
    cd ~/Desktop/ros2-humble-biorobub
    docker-compose up -d
    docker exec -it pc_humble bash
    code .                     # open VSCode inside the container
    ros2 topic list
    ````
- Open `.bashrc` file inside the container and verify it contains:
    ````bash
    source /opt/ros/humble/setup.bash
    source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash
    source ~/Desktop/ROS2_rUBot_mecanum_ws/install/setup.bash
    cd ~/Desktop/ROS2_rUBot_mecanum_ws
    export GAZEBO_MODEL_PATH=~/Desktop/ROS2_rUBot_mecanum_ws/src/my_robot_bringup/models:$GAZEBO_MODEL_PATH
    export QT_QPA_PLATFORM=xcb           # Best for RVIZ2
    export ROS_DOMAIN_ID=1               # group/domain ID
    export ROS_LOCALHOST_ONLY=0          # allow communication with other machines
    export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
    export CYCLONEDDS_URI=file:///home/student/Desktop/ROS2_rUBot_mecanum_ws/network_config/cyclonedds_pc.xml
    ````

- To stop the container:
    ````bash
    docker-compose down
    ````
- To see the Images and Containers:
    ````bash
    docker ps -a               # containers
    docker images              # images
    ````

You are ready to work with ROS2 Humble on Docker!
