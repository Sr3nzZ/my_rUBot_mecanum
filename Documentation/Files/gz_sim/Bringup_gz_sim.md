# GZ sim

Models on `my_robot_bringup/Models`

Launch:
````bash
ros2 launch my_robot_bringup my_robot_bringup_gz.launch.py world:=square_sign_ign.world robot:=rubot_mecanum x:=0.0 y:=0.0 w:=90
````
In .bashrc add:
````bash
export GZ_SIM_RESOURCE_PATH=$(ros2 pkg prefix my_robot_bringup)/share/my_robot_bringup/models:${GZ_SIM_RESOURCE_PATH}
o
export IGN_GAZEBO_RESOURCE_PATH=/path/al/teu/models:$IGN_GAZEBO_RESOURCE_PATH
````