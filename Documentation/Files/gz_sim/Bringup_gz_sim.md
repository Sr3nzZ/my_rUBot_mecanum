# GZ sim

Models on `my_robot_bringup/Models`

Launch:
````bash
ros2 launch my_robot_bringup rubot_gz_bringup.launch.py
````
In .bashrc add:
````bash
export GZ_SIM_RESOURCE_PATH=$(ros2 pkg prefix my_robot_bringup)/share/my_robot_bringup/models:${GZ_SIM_RESOURCE_PATH}
o
export IGN_GAZEBO_RESOURCE_PATH=/path/al/teu/models:$IGN_GAZEBO_RESOURCE_PATH
````