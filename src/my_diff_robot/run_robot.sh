#!/bin/bash

# підключаємо ROS2 workspace
source ~/ros2_ws/install/setup.bash

echo "Starting safety node..."

# запускаємо safety_node у фоні
ros2 run my_diff_robot safety_node.py &


sleep 0.5

echo "Starting teleop..."

# запускаємо teleop
ros2 run my_diff_robot simple_teleop.py

echo "Teleop closed. Stopping safety node..."

# зупиняємо safety node
pkill -f safety_node.py
