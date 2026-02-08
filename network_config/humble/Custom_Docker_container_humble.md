## UB custom Docker-based ROS2 Humble environment

We have designed a University of Barcelona custom Docker-based ROS 2 Humble environment to simplify student access to ROS 2 and ensure platform-independent workflows in robotics courses.

A proper Docker Image has been created with the custom configuration on Dockerfile and uploaded to my DockerHub account (https://hub.docker.com/r/manelpuig/ros2-humble-biorobub-pc).

**Students** in the lab they only need to:
- Verify you have `Docker Engine` and `Docker Compose plugin` from the official Docker repositories.
- Copy the contents of `my_rUBot_mecanum/network_config/humble/` in a `~/Desktop/rob` folder on Linux PC
- review on:
    - `docker-compose.yaml` file: 
        - `ROS_DOMAIN_ID=1` variable to match your Group number.
        - `ROS_STATIC_PEERS=192.168.1.14` variable to match your robot ID.
    - `cyclonedds_pc.xml` file: verify `<NetworkInterface name="wlp1s0"/>`.
    - `cyclonedds_robot.xml` file: verify `<NetworkInterface name="wlan0"/>`.
- Open a terminal in the `~/Desktop/rob/` folder and run:
    ````bash
    xhost +local:root            # allow X11 for Docker (lab use only)
    cd ~/Desktop/rob
    docker compose up -d
    docker exec -it pc_humble bash
    code .                     # open VSCode inside the container
    ros2 topic list
    ````
- Verify the environment variables are correctly set by checking the container startup output.

- To stop the container:
    ````bash
    docker compose down
    ````
- To see the Images and Containers:
    ````bash
    docker ps -a               # containers
    docker images              # images
    ````

You are ready to work with ROS2 Humble on Docker!

### Quick checklist if communication does not work

- PC and robot use the same ROS_DOMAIN_ID
- `ROS_STATIC_PEERS` contains the correct IP of the other machine
- `ROS_AUTOMATIC_DISCOVERY_RANGE=OFF` is set on both sides
- Correct NetworkInterface is set in cyclonedds_*.xml
- PC container is started with `network_mode: host`

