# ROS2 Differential Drive Robot with Safety Controller

## 📖 Overview
This project implements a ROS2-based control system for a differential drive robot equipped with a LiDAR sensor. It features a robust **Safety Controller** that acts as an interceptor between user teleoperation commands and the robot's drive controller. The primary goal is to provide directional collision avoidance, ensuring the robot reliably stops before hitting obstacles while maintaining fluid driveability in open spaces.

## 📂 Project Structure

```text
my_diff_robot/
├── config/
│   ├── controllers.yaml
│   └── gz_bridge.yaml
├── launch/
│   └── robot.launch.py
├── rviz/
│   └── robot.rviz
├── scripts/
│   ├── safety_node.py        # Implements collision avoidance logic
│   └── simple_teleop.py     
├── urdf/
│   └── robot.urdf
├── worlds/
│   └── empty.sdf
├── CMakeLists.txt
├── package.xml
├── run_robot.sh              # Script to build and run the containerized app
├── Dockerfile                # Container definition
└── README.md
