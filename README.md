# ROS2 Differential Drive Robot with Safety Controller

## Overview
This project implements a ROS2-based control system for a differential drive robot equipped with a LiDAR sensor. It features a robust **Safety Controller** that acts as an interceptor between user teleoperation commands and the robot's drive controller. The primary goal is to provide directional collision avoidance, ensuring the robot reliably stops before hitting obstacles while maintaining fluid driveability in open spaces.

## Project Structure

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
├── Dockerfile                
└── README.md
```
  ## Design Description & Key Choices
The solution is designed around an **Interceptor Pattern** to ensure safety without modifying the core drive controllers:

* **Directional Safety Node:** The `safety_node.py` subscribes to both `/scan` (LiDAR) and `/teleop_cmd_vel`. It evaluates the intended direction of travel (forward or reverse) and calculates the minimum distance to obstacles in that specific direction.
* **Proportional Braking:** Instead of a sudden hard stop, the robot begins to smoothly decelerate when an obstacle is within 1.1 meters (0.5m stop distance + 0.6m margin).
* **Data Sanitization:** The LiDAR processor safely ignores `inf`, `NaN`, and physically impossible values (e.g., `< 0.05m`), ensuring the controller doesn't crash or behave erratically due to sensor noise.

### How the Stopping Mechanism Works
The obstacle avoidance logic runs continuously at 20Hz, acting as a dynamic safety filter between the operator and the robot's motors:

1. **Directional Awareness:** The 360° LiDAR scan is split into a **Front Hemisphere** (-90° to +90°) and a **Rear Hemisphere**. The node continuously tracks the minimum distance to any valid obstacle in both zones.
2. **Intent Matching:** When a teleop command is received, the node checks the intended direction of travel. If driving forward (`linear.x > 0`), it only evaluates the front distance. If reversing (`linear.x < 0`), it evaluates the rear distance.
3. **Three-Tier Safety Zones:**
   * **Free Drive (> 1.1m):** The user's velocity command is passed through directly to the controllers.
   * **Proportional Braking (0.5m to 1.1m):** As the robot approaches the obstacle, its speed is mathematically scaled down based on the distance. This ensures smooth deceleration instead of jerky movements.
   * **Hard Stop (<= 0.5m):** If the obstacle breaches the 0.5-meter threshold, the `linear.x` velocity is strictly overwritten to `0.0`. The robot physically cannot drive further towards the obstacle, but the logic fully allows the user to rotate or drive away in the opposite, safe direction.

## How to Run Locally

This project is fully containerized for easy deployment. Ensure you have Docker installed on your host system.

**1. Clone the repository:**
```bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_NAME>
```
**2. Build and start the container:**
Navigate to the project directory and run the provided shell script. This will automatically build the Docker image (using the `Dockerfile`) and start the container with the necessary volume mounts and network configurations.

```bash
cd ~/ros2_ws/src/my_diff_robot
chmod +x run_robot.sh
./run_robot.sh
```
**3. Launch the Robot System:**
Once the container is running and you are inside its terminal, launch the ROS2 environment:

```bash
ros2 launch my_diff_robot robot.launch.py
```
## Demo Video

[Watch the demonstration video on Google Drive](https://drive.google.com/file/d/19fYYjvDl7gmC_i0PENhkLgBdngRZbt5G/view?usp=drive_link)
